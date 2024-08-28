import os

import pytest
from localstack.pro.core.services.serverlessrepo.provider import PREDEFINED_APPS
from localstack.testing.pytest import markers
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition
from localstack_snapshot.snapshots import SnapshotSession


def create_serverless_application(
    client, author: str = "LocalStack", description: str = "", name: str = "LocalStackApp"
):
    return client.create_application(Author=author, Description=description, Name=name)


class TestServerlessRepo:
    @markers.aws.needs_fixing
    def test_crud_applications(self, aws_client):
        result = create_serverless_application(aws_client.serverlessrepo)
        application_id = result["ApplicationId"]
        assert application_id
        assert result["Name"] == "LocalStackApp"

        result = aws_client.serverlessrepo.list_applications()
        assert len(result["Applications"]) == 1
        assert result["Applications"][0]["ApplicationId"] == application_id

        result = aws_client.serverlessrepo.get_application(ApplicationId=application_id)
        assert result["Name"] == "LocalStackApp"
        assert result["ApplicationId"] == application_id
        aws_client.serverlessrepo.delete_application(ApplicationId=application_id)

    @markers.aws.needs_fixing
    def test_crud_application_versions(self, aws_client):
        result = create_serverless_application(aws_client.serverlessrepo)
        application_id = result["ApplicationId"]

        result = aws_client.serverlessrepo.create_application_version(
            ApplicationId=application_id, SemanticVersion="1.1.100"
        )
        assert result["ApplicationId"] == application_id
        assert result["CreationTime"]

        result = aws_client.serverlessrepo.list_application_versions(ApplicationId=application_id)
        assert len(result["Versions"]) == 1
        assert result["Versions"][0]["ApplicationId"] == application_id
        aws_client.serverlessrepo.delete_application(ApplicationId=application_id)
        with pytest.raises(Exception) as e:
            aws_client.serverlessrepo.list_application_versions(ApplicationId=application_id)
        assert "Unable to find" in str(e.value)

    @markers.aws.validated
    def test_lookup_predefined_application(self, aws_client):
        """
        currently (2023-08-22) there are 387 versions available for this application
        """
        result = (
            aws_client.serverlessrepo.get_paginator("list_application_versions")
            .paginate(ApplicationId=PREDEFINED_APPS[0])
            .build_full_result()
        )
        version1_1_129 = [v for v in result["Versions"] if v["SemanticVersion"] == "1.1.129"][0]
        assert version1_1_129["ApplicationId"] == PREDEFINED_APPS[0]
        assert version1_1_129["SemanticVersion"] == "1.1.129"

    @markers.aws.needs_fixing
    def test_crud_formation_template(self, aws_client):
        # we rely on the pre-defined app for this test
        result = aws_client.serverlessrepo.create_cloud_formation_template(
            ApplicationId=PREDEFINED_APPS[0], SemanticVersion="1.1.129"
        )
        assert result["ApplicationId"] == PREDEFINED_APPS[0]
        assert result["Status"] == "ACTIVE"
        template_url = result["TemplateUrl"]
        template_id = result["TemplateId"]

        result = aws_client.serverlessrepo.get_cloud_formation_template(
            ApplicationId=PREDEFINED_APPS[0], TemplateId=template_id
        )
        assert result["TemplateId"] == template_id
        assert result["TemplateUrl"] == template_url

    # TODO: validate
    # TODO: what's the purpose of this test?
    @markers.aws.needs_fixing
    def test_create_cloud_formation_change_set(self, aws_client, cleanups):
        application_id = PREDEFINED_APPS[0]
        cleanups.append(
            lambda: aws_client.serverlessrepo.delete_application(ApplicationId=application_id)
        )

        # what's the purpose of the create_cloud_formation_template call?
        result = aws_client.serverlessrepo.create_cloud_formation_template(
            ApplicationId=PREDEFINED_APPS[0], SemanticVersion="1.1.129"
        )
        assert result["ApplicationId"] == application_id

        # TODO: shouldn't the template returned by the result above be used below?
        #   see => result['TemplateUrl']

        stack_name = f"stack-{short_uid()}"
        fn_name = f"sar-test-fn-{short_uid()}"
        result = aws_client.serverlessrepo.create_cloud_formation_change_set(
            ApplicationId=application_id,
            StackName=stack_name,
            ChangeSetName="changeSetName",
            Capabilities=["CAPABILITY_AUTO_EXPAND"],
            ParameterOverrides=[
                {"Name": "endpoint", "Value": "unknown"},
                {"Name": "functionName", "Value": fn_name},
            ],
        )
        assert result["ApplicationId"] == application_id

    @markers.aws.validated
    def test_not_existing_version(self, aws_client):
        region = aws_client.serverlessrepo.meta.region_name
        account_id = aws_client.sts.get_caller_identity()["Account"]
        app_name_not_existing = f"invalid-app-{short_uid()}"
        with pytest.raises(aws_client.serverlessrepo.exceptions.NotFoundException):
            aws_client.serverlessrepo.list_application_versions(
                ApplicationId=f"arn:aws:serverlessrepo:{region}:{account_id}:applications/{app_name_not_existing}"
            )


def _load_template(template_file: str) -> str:
    return load_file(os.path.join(os.path.dirname(__file__), "templates", template_file))


TEMPLATE_BODY_NO_RESOURCES = """
Transform: something
"""
TEMPLATE_BODY_NO_TRANSFORM = """
Resources:
    MyTopic:
        Type: AWS::SNS::Topic
"""
TEMPLATE_BODY_INVALID_TRANSFORM = """
Transform: something
Resources:
    MyTopic:
        Type: AWS::SNS::Topic
"""
TEMPLATE_BODY_VALID = """
Transform: 'AWS::Serverless-2016-10-31'
Resources:
    MyTopic:
        Type: AWS::SNS::Topic
"""


class TestServerlessRepoParity:
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..ApplicationId", "$..IsVerifiedAuthor", "$..Labels"]
    )
    @markers.aws.validated
    def test_minimal_app_without_version(self, aws_client, cleanups, snapshot):
        """Minimal application without publishing a semantic version"""
        slsrepo = aws_client.serverlessrepo
        app_name = f"app-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(app_name, replacement="<app-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="TemplateUrl", value_replacement="<template-url>", reference_replacement=False
            ),
            priority=-1,
        )
        create_application = slsrepo.create_application(
            Author="LocalStack", Description="Testing", Name=app_name
        )
        app_id = create_application["ApplicationId"]
        cleanups.append(lambda: slsrepo.delete_application(ApplicationId=app_id))
        snapshot.match("create_application", create_application)

    @markers.snapshot.skip_snapshot_verify(
        paths=["$..ApplicationId", "$..IsVerifiedAuthor", "$..Labels", "$..Version"]
    )
    @markers.aws.validated
    def test_minimal_app_with_version(self, aws_client, cleanups, snapshot):
        """Minimal application with an automatically created application version"""
        slsrepo = aws_client.serverlessrepo
        app_name = f"app-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(app_name, replacement="<app-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="TemplateUrl", value_replacement="<template-url>", reference_replacement=False
            ),
            priority=-1,
        )
        create_application = slsrepo.create_application(
            Author="LocalStack",
            Description="Testing",
            Name=app_name,
            SemanticVersion="0.0.1",
            TemplateBody=TEMPLATE_BODY_VALID,
        )
        app_id = create_application["ApplicationId"]
        cleanups.append(lambda: slsrepo.delete_application(ApplicationId=app_id))
        snapshot.match("create_application", create_application)
        snapshot.match(
            "get_application_version",
            slsrepo.get_application(ApplicationId=app_id, SemanticVersion="0.0.1"),
        )
        snapshot.match("get_application", slsrepo.get_application(ApplicationId=app_id))

    @pytest.mark.skip(reason="needs to be implemented")
    @markers.aws.validated
    def test_template_validation(self, aws_client, cleanups, snapshot):
        """
        AWS validates certain things about the serverless template which we try to capture here
        """
        slsrepo = aws_client.serverlessrepo
        app_name = f"app-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(app_name, replacement="<app-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="TemplateUrl", value_replacement="<template-url>", reference_replacement=False
            ),
            priority=-1,
        )
        app = slsrepo.create_application(
            Author="LocalStack",
            Description="Testing",
            Name=app_name,
            TemplateBody="random gibberish",  # ! it doesn't care here what we pass if we don't also pass SemanticVersion
        )
        app_id = app["ApplicationId"]
        cleanups.append(lambda: slsrepo.delete_application(ApplicationId=app_id))
        snapshot.match("create_application", app)

        # for templates specified in create_application_version the service validates it

        # needs to be a yaml/json dict
        with pytest.raises(slsrepo.exceptions.BadRequestException) as e:
            slsrepo.create_application_version(
                ApplicationId=app_id, SemanticVersion="0.0.1", TemplateBody="invalid"
            )
        snapshot.match("version_template_validation_exc_nodict", e.value.response)

        # resources need to exist
        with pytest.raises(slsrepo.exceptions.BadRequestException) as e:
            slsrepo.create_application_version(
                ApplicationId=app_id,
                SemanticVersion="0.0.1",
                TemplateBody=TEMPLATE_BODY_NO_RESOURCES,
            )
        snapshot.match("version_template_validation_exc_nores", e.value.response)

        # transform field needs to exist
        with pytest.raises(slsrepo.exceptions.BadRequestException) as e:
            slsrepo.create_application_version(
                ApplicationId=app_id,
                SemanticVersion="0.0.1",
                TemplateBody=TEMPLATE_BODY_NO_TRANSFORM,
            )
        snapshot.match("version_template_validation_exc_notransform", e.value.response)

        # invalid transform (only supports 'AWS::Serverless-2016-10-31')
        with pytest.raises(slsrepo.exceptions.BadRequestException) as e:
            slsrepo.create_application_version(
                ApplicationId=app_id,
                SemanticVersion="0.0.1",
                TemplateBody=TEMPLATE_BODY_INVALID_TRANSFORM,
            )
        snapshot.match("version_template_validation_exc_invalidtransform", e.value.response)

        # valid
        create_application_version = slsrepo.create_application_version(
            ApplicationId=app_id, SemanticVersion="0.0.1", TemplateBody=TEMPLATE_BODY_VALID
        )
        snapshot.match("create_application_version", create_application_version)

    @pytest.mark.skip(reason="needs to be implemented")
    @markers.aws.validated
    def test_serverlessrepo_lifecycle(self, aws_client, cleanups, snapshot: SnapshotSession):
        """
        Tests the general lifecycle and certain validations along the way (e.g. conflicts & input validations)

        1. Create Serverless Application (+ implicitly create a 0.0.1 version)
        2. Create another Application Version (0.0.2)
        3. Create cloudformation change set from the application
        4. Delete the Serverless Application

        TODO: duplicate name => error
        TODO: test TemplateUrl
        TODO: test Urls (e.g. LicenseUrl needs to be an S3 URI)
        TODO: test public repo
        """
        slsrepo = aws_client.serverlessrepo
        app_name = f"app-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.regex(app_name, replacement="<app-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="TemplateUrl", value_replacement="<template-url>", reference_replacement=False
            ),
            priority=-1,
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="LicenseUrl", value_replacement="<license-url>", reference_replacement=False
            ),
            priority=-1,
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="ReadmeUrl", value_replacement="<readme-url>", reference_replacement=False
            ),
            priority=-1,
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                key="HomePageUrl", value_replacement="<homepage-url>", reference_replacement=False
            ),
            priority=-1,
        )

        create_application = slsrepo.create_application(
            Author="LocalStack",
            Description="Testing",
            Name=app_name,
            HomePageUrl="https://localstack.cloud",
            Labels=["label1", "label2"],
            LicenseBody="License",
            # would be automatically generated to point to license body
            # LicenseUrl="?",
            ReadmeBody="readme",
            # would be automatically generated to point to readme body
            # ReadmeUrl="?",
            SemanticVersion="0.0.1",
            # SourceCodeArchiveUrl="?",
            SourceCodeUrl="https://localstack.cloud/codeurl",
            # SpdxLicenseId="?",
            TemplateBody=TEMPLATE_BODY_VALID,
            # would be automatically generated to point to template body
            # TemplateUrl="?"  # TODO: test with a URL, probably same behavior as in CFn where this needs to be an s3 URI
        )
        app_id = create_application["ApplicationId"]
        cleanups.append(lambda: slsrepo.delete_application(ApplicationId=app_id))
        snapshot.match("create_application", create_application)

        # serverless repo enforces correct semver format
        with pytest.raises(slsrepo.exceptions.BadRequestException) as e:
            slsrepo.create_application_version(ApplicationId=app_id, SemanticVersion="?")
        # serverless repo enforces correct semver format
        create_application_version = slsrepo.create_application_version(
            ApplicationId=app_id,
            SemanticVersion="0.0.2",
            TemplateBody=TEMPLATE_BODY_VALID,
            SourceCodeUrl="https://localstack.cloud/codeurl",
        )
        snapshot.match("create_application_version", create_application_version)

        v001 = slsrepo.get_application(ApplicationId=app_id, SemanticVersion="0.0.1")
        snapshot.match("v001_get_application", v001)
        v002 = slsrepo.get_application(ApplicationId=app_id, SemanticVersion="0.0.2")
        snapshot.match("v002_get_application", v002)

        # this is flaky(!) otherwise since sometimes it only shows one version
        poll_condition(
            lambda: len(slsrepo.list_application_versions(ApplicationId=app_id)["Versions"]) == 2
        )
        application_versions = slsrepo.list_application_versions(ApplicationId=app_id)
        snapshot.match("list_application_versions", application_versions)
        list_applications = [
            app
            for app in slsrepo.list_applications()["Applications"]
            if app["ApplicationId"] == app_id
        ]
        snapshot.match("list_applications", {"Applications": list_applications})
        # TODO: filter and snapshot

        app_dependencies = slsrepo.list_application_dependencies(
            ApplicationId=app_id, SemanticVersion="0.0.2"
        )
        snapshot.match("app_dependencies", app_dependencies)

        # application policy CRUD
        app_policy_empty = slsrepo.get_application_policy(ApplicationId=app_id)
        snapshot.match("app_policy_empty", app_policy_empty)

        # make the app public
        put_policy_public = slsrepo.put_application_policy(
            ApplicationId=app_id, Statements=[{"Actions": ["Deploy"], "Principals": ["*"]}]
        )
        snapshot.match("put_policy_public", put_policy_public)

        put_application_policy = slsrepo.put_application_policy(
            ApplicationId=app_id,
            Statements=[{"Actions": ["Deploy"], "Principals": ["000000000000"]}],
        )
        snapshot.match("put_application_policy", put_application_policy)

        app_policy_nonempty = slsrepo.get_application_policy(ApplicationId=app_id)
        snapshot.match("app_policy_nonempty", app_policy_nonempty)

        # reset the application policy (make it private)
        put_application_policy_private = slsrepo.put_application_policy(
            ApplicationId=app_id, Statements=[]
        )
        snapshot.match("put_application_policy_private", put_application_policy_private)
        app_policy_private = slsrepo.get_application_policy(ApplicationId=app_id)
        snapshot.match("app_policy_private", app_policy_private)

        # cloudformation
        cfn_template = slsrepo.create_cloud_formation_template(
            ApplicationId=app_id, SemanticVersion="0.0.2"
        )
        template_id = cfn_template["TemplateId"]
        # possible statuses: "ACTIVE", "EXPIRED", "PREPARING"
        poll_condition(
            lambda: slsrepo.get_cloud_formation_template(
                ApplicationId=app_id, TemplateId=template_id
            )["Status"]
            != "PREPARING"
        )
        get_cfn_template = slsrepo.get_cloud_formation_template(
            ApplicationId=app_id, TemplateId=template_id
        )
        assert get_cfn_template["Status"] == "ACTIVE"
        snapshot.match("get_cloud_formation_template", get_cfn_template)

        stack_name = f"sls-test-stack-{short_uid()}"
        # TODO: test specifying different TemplateId values
        cs_name = f"sls-test-cs-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(stack_name, "<stack-name>"))
        snapshot.add_transformer(snapshot.transform.regex(cs_name, "<changeset-name>"))
        change_set = slsrepo.create_cloud_formation_change_set(
            ApplicationId=app_id, StackName=stack_name, ChangeSetName=cs_name
        )
        cleanups.append(lambda: aws_client.cloudformation.delete_stack(StackName=stack_name))
        snapshot.match("create_cloud_formation_change_set", change_set)
        change_set_id_uuid = change_set["ChangeSetId"].rpartition("/")[-1]
        stack_id_uuid = change_set["StackId"].rpartition("/")[-1]
        snapshot.add_transformer(
            snapshot.transform.regex(change_set_id_uuid, "<change_set_id_uuid>")
        )
        snapshot.add_transformer(snapshot.transform.regex(stack_id_uuid, "<stack_id_uuid>"))

        # delete the application and verify responses
        slsrepo.delete_application(ApplicationId=app_id)
        with pytest.raises(slsrepo.exceptions.NotFoundException) as e:
            slsrepo.list_application_versions(ApplicationId=app_id)
        snapshot.match("list_application_versions_none_exc", e.value.response)
        with pytest.raises(slsrepo.exceptions.NotFoundException) as e:
            slsrepo.get_application(ApplicationId=app_id)
        snapshot.match("get_application_none_exc", e.value.response)

        # cloudformation changeset is still there after app deletion
        describe_change_set = aws_client.cloudformation.describe_change_set(
            ChangeSetName=change_set["ChangeSetId"]
        )
        snapshot.match("describe_change_set", describe_change_set)

    # remaining / untested operations
    # def test_todo(self, aws_client):
    #     aws_client.serverlessrepo.generate_presigned_url()
    #     aws_client.serverlessrepo.update_application(ApplicationId="?", Author="?", Description="?", HomePageUrl="?", Labels=["?"], ReadmeBody="?", ReadmeUrl="?")
    #     aws_client.serverlessrepo.unshare_application(ApplicationId="?", OrganizationId="?")
