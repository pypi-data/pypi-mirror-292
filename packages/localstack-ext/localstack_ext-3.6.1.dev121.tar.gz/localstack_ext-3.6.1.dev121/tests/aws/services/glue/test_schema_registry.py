import logging
from time import sleep
from typing import List

import pytest
from localstack.pro.core.aws.api.glue import (
    Compatibility,
    SchemaDefinitionString,
    SchemaId,
    SchemaVersionNumber,
    SchemaVersionStatus,
)
from localstack.pro.core.services.glue.models import DEFAULT_REGISTRY_NAME
from localstack.testing.pytest import markers
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)

# person_age is forward compatible to person, but not backward compatible
person_age = '{"type":"record","namespace":"Test","name":"Person","fields":[{"name":"Name","type":"string"},{"name":"Age","type":"int"}]}'
# person is backward compatible to person_age and person_age_salary, but not forward compatible
person = '{"type":"record","namespace":"Test","name":"Person","fields":[{"name":"Name","type":"string"}]}'
# person_salary is full compatible to person
person_salary = '{"type":"record","namespace":"Test","name":"Person","fields":[{"name":"Name","type":"string"},{"name":"Salary","type":["null", "int"], "default": null}]}'
# person_age_salary is backwards compatible to person_age
person_age_salary = '{"type":"record","namespace":"Test","name":"Person","fields":[{"name":"Name","type":"string"},{"name":"Age","type":"int"},{"name":"Salary","type":["null", "int"], "default": null}]}'


class TestGlueSchemaRegistry:
    @markers.aws.unknown
    def test_schema_version_crud(self, glue_create_schema, aws_client):
        # Create the schema versions
        schema_name = glue_create_schema(
            DataFormat="AVRO", Compatibility="NONE", SchemaDefinition=person
        )
        aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person_age,
        )
        aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person_salary,
        )
        aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person_age_salary,
        )

        # List schema versions
        list_schema_versions_1 = aws_client.glue.list_schema_versions(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            MaxResults=1,
        )
        assert len(list_schema_versions_1["Schemas"]) == 1
        assert "NextToken" in list_schema_versions_1
        list_schema_versions_2 = aws_client.glue.list_schema_versions(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME)
        )
        assert len(list_schema_versions_2["Schemas"]) == 4

        # Deleting a checkpoint raises an error
        with pytest.raises(aws_client.glue.exceptions.InvalidInputException):
            aws_client.glue.delete_schema_versions(
                SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                Versions="1-6",
            )
        # Deleting other versions (even ones which do not exist) is successful
        aws_client.glue.delete_schema_versions(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            Versions="2-9",
        )
        list_schema_versions_1 = aws_client.glue.list_schema_versions(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME)
        )
        assert len(list_schema_versions_1["Schemas"]) == 1

    @markers.aws.validated
    @pytest.mark.parametrize(
        "compatibility,first_schema,intermediate_schemas,new_schema,expected_status",
        [
            # None allows all updates
            [Compatibility.NONE, person_age, None, person, SchemaVersionStatus.AVAILABLE],
            [Compatibility.NONE, person, None, person_age, SchemaVersionStatus.AVAILABLE],
            # person is backward compatible to person_age, but not the other way around
            [Compatibility.BACKWARD, person_age, None, person, SchemaVersionStatus.AVAILABLE],
            [Compatibility.BACKWARD, person, None, person_age, SchemaVersionStatus.FAILURE],
            # person_age is forward compatible to person, but not the other way around
            [Compatibility.FORWARD, person, None, person_age, SchemaVersionStatus.AVAILABLE],
            [Compatibility.FORWARD, person_age, None, person, SchemaVersionStatus.FAILURE],
            # Full combines backward and forward, both combinations need to fail for person and person_age
            [Compatibility.FULL, person, None, person_age, SchemaVersionStatus.FAILURE],
            [Compatibility.FULL, person_age, None, person, SchemaVersionStatus.FAILURE],
            # ... but should be successful for person and person_salary
            [Compatibility.FULL, person, None, person_salary, SchemaVersionStatus.AVAILABLE],
            [Compatibility.FULL, person_salary, None, person, SchemaVersionStatus.AVAILABLE],
            # Check transitive forward compatibility
            [
                Compatibility.BACKWARD_ALL,
                person_age_salary,
                [person_age],
                person,
                SchemaVersionStatus.AVAILABLE,
            ],
            [
                Compatibility.BACKWARD_ALL,
                person_age_salary,
                [person],
                person_age,
                SchemaVersionStatus.FAILURE,
            ],
            # Check transitive forward compatibility
            [
                Compatibility.FORWARD_ALL,
                person,
                [person_age_salary],
                person_age,
                SchemaVersionStatus.AVAILABLE,
            ],
            [
                Compatibility.FORWARD_ALL,
                person_age,
                [person_age_salary],
                person,
                SchemaVersionStatus.FAILURE,
            ],
            # Check transitive full compatibility
            [
                Compatibility.FULL_ALL,
                person,
                [person_age_salary],
                person_salary,
                SchemaVersionStatus.AVAILABLE,
            ],
            [
                Compatibility.FULL_ALL,
                person,
                [person_salary],
                person_age_salary,
                SchemaVersionStatus.FAILURE,
            ],
        ],
    )
    def test_register_avro_schema_version_compatibilities(
        self,
        glue_create_schema,
        compatibility: Compatibility,
        first_schema: SchemaDefinitionString,
        intermediate_schemas: List[SchemaDefinitionString],
        new_schema: SchemaDefinitionString,
        expected_status: SchemaVersionStatus,
        aws_client,
    ):
        # Create the initial schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=first_schema, Compatibility=compatibility
        )

        # Register the intermediate versions
        if intermediate_schemas:
            for intermediate_schema_version in intermediate_schemas:
                aws_client.glue.register_schema_version(
                    SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                    SchemaDefinition=intermediate_schema_version,
                )

        # Wait a second to avoid concurrent modification exceptions
        sleep(1)

        # Register the version we are interested in
        response = aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=new_schema,
        )
        version_id = response["SchemaVersionId"]

        # check the status of the created version (wait for the status to change from pending to the expected state)
        def _check(*_):
            schema_version = aws_client.glue.get_schema_version(SchemaVersionId=version_id)
            LOG.debug("Current Schema Version Status: %s", schema_version["Status"])
            assert schema_version["Status"] == expected_status

        retry(_check, retries=5, sleep=1)

    @markers.aws.validated
    def test_duplicate_schema_version_not_created(self, glue_create_schema, aws_client):
        # Create the initial schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person, Compatibility=Compatibility.NONE
        )
        response = aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person,
        )
        assert response["VersionNumber"] == 1

    @markers.aws.validated
    def test_compatibility_disabled_raises_on_new_version(self, glue_create_schema, aws_client):
        # Create the initial schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person, Compatibility=Compatibility.DISABLED
        )
        # Make an exception is raised on any updates
        with pytest.raises(aws_client.glue.exceptions.InvalidInputException):
            aws_client.glue.register_schema_version(
                SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                SchemaDefinition=person_age,
            )

    @markers.aws.validated
    def test_update_schema_to_lower_than_checkpoint(self, glue_create_schema, aws_client):
        # Create the initial schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Create a second version
        new_version = aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person,
        )
        # Set the checkpoint to the new version
        aws_client.glue.update_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=new_version["VersionNumber"]),
        )
        # Make sure it's forbidden to set the checkpoint to a lower version
        with pytest.raises(aws_client.glue.exceptions.InvalidInputException):
            aws_client.glue.update_schema(
                SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            )

    @markers.aws.validated
    def test_update_schema_only_description(self, glue_create_schema, aws_client):
        # Create the schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Set a new description
        aws_client.glue.update_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            Description="New Description",
        )
        # Check that the description has been updated
        schema = aws_client.glue.get_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME)
        )
        assert schema["Description"] == "New Description"

    @markers.aws.validated
    def test_update_schema_compatibility_without_version(self, glue_create_schema, aws_client):
        # Create the schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Make sure you need to add a version when changing the compatibility
        with pytest.raises(aws_client.glue.exceptions.InvalidInputException):
            aws_client.glue.update_schema(
                SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                Compatibility=Compatibility.BACKWARD,
            )

    @markers.aws.validated
    def test_update_schema_compatibility_with_same_value(self, glue_create_schema, aws_client):
        # Create the schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Make sure it's forbidden to set the same compatibility again
        with pytest.raises(aws_client.glue.exceptions.InvalidInputException):
            aws_client.glue.update_schema(
                SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
                SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
                Compatibility=Compatibility.BACKWARD,
            )

    @markers.aws.validated
    def test_update_schema_compatibility(self, glue_create_schema, aws_client):
        # Create the schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Set a new compatibility
        aws_client.glue.update_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            Compatibility=Compatibility.FORWARD,
        )
        # Check that the compatibility has been updated
        schema = aws_client.glue.get_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME)
        )
        assert schema["Compatibility"] == Compatibility.FORWARD

    @markers.aws.validated
    def test_update_schema(self, glue_create_schema, aws_client):
        # Create the initial schema / version
        schema_name = glue_create_schema(
            DataFormat="AVRO", SchemaDefinition=person_age, Compatibility=Compatibility.BACKWARD
        )
        # Create a second version
        new_version = aws_client.glue.register_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaDefinition=person,
        )
        # Set the checkpoint to the new version
        aws_client.glue.update_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=new_version["VersionNumber"]),
        )
        # Check that the checkpoint has been updated
        schema = aws_client.glue.get_schema(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME)
        )
        assert schema["SchemaCheckpoint"] == new_version["VersionNumber"]
