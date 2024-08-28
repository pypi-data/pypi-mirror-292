import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestResourceAccessManager:
    @markers.aws.needs_fixing
    def test_list_resource_types(self, snapshot, aws_client):
        # LS returns resources types in lowercase. This is a design choice to ensure case-insensitivity.
        # To make this AWS validated, resource types need to be in CamelCase
        result = aws_client.ram.list_resource_types()

        # Sort response for easier comparison
        result["resourceTypes"] = sorted(result["resourceTypes"], key=lambda x: x["resourceType"])
        snapshot.match("list-resource-types", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        path=[
            "$..permissions..isResourceTypeDefault",
            "$..permissions..tags",
            "$..permissions..version",
        ]
    )
    def test_aws_managed_permissions(self, snapshot, aws_client):
        result = aws_client.ram.list_permissions(permissionType="AWS")
        snapshot.match("list-aws-managed-permissions", result)

    @markers.aws.validated
    def test_create_permission(self, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.key_value("name"))
        snapshot.add_transformer(snapshot.transform.key_value("arn"))

        name = short_uid()
        result = aws_client.ram.create_permission(
            name=name,
            resourceType="appsync:Apis",
            policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL"}',
            tags=[{"key": "foo", "value": "bar"}],
        )
        snapshot.match("create-permission", result)
        arn = result["permission"]["arn"]

        # Must raise if permission name exists
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_permission(
                name=name,
                resourceType="appsync:apis",
                policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL"}',
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "PermissionAlreadyExistsException"
        assert err["Message"] == f"The permission {arn} already exists."

        # Ensure GetPermission
        result = aws_client.ram.get_permission(permissionArn=arn)
        snapshot.match("get-permission", result)

        # Ensure ListPermissions scopes are equivalent
        result = aws_client.ram.list_permissions(permissionType="LOCAL")
        snapshot.match("list-permissions", result)
        result = aws_client.ram.list_permissions(permissionType="CUSTOMER_MANAGED")
        snapshot.match("list-permissions-2", result)

        # Raise if bad scope is used for ListPermissions
        with pytest.raises(ClientError) as exc:
            aws_client.ram.list_permissions(permissionType="XYZ")
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == "XYZ is not a valid scope. Must be one of: ALL, AWS, LOCAL."

        # Ensure DeletePermission
        result = aws_client.ram.delete_permission(permissionArn=arn)
        snapshot.match("delete-permission", result)

        # Ensure ListPermissions after deletion
        result = aws_client.ram.list_permissions(permissionType="CUSTOMER_MANAGED")
        snapshot.match("list-permissions-3", result)

        # Must raise if the resource type is not supported by RAM
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_permission(
                name=short_uid(),
                resourceType="ec2:Instance",
                policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL"}',
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == "Invalid resource type: ec2:Instance"

        # Must raise if policy fields aren't properly formatted
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_permission(
                name=short_uid(),
                resourceType="appsync:Apis",
                policyTemplate='{"Effect": "Allow", "action": "appsync:SourceGraphQL"}',
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidPolicyException"
        assert err["Message"] == "InvalidPolicy: Invalid policy format."

        # Must raise if policy denies
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_permission(
                name=short_uid(),
                resourceType="appsync:Apis",
                policyTemplate='{"Effect": "Deny", "Action": "appsync:SourceGraphQL"}',
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidPolicyException"
        assert err["Message"] == "InvalidPolicy: Only the Allow effect is supported"

        # Must raise if policy contains additional fields
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_permission(
                name=short_uid(),
                resourceType="appsync:Apis",
                policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL", "Resource": "*"}',
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidPolicyException"
        assert (
            err["Message"]
            == "InvalidPolicy: Only effect, action, and condition blocks can exist in permission policy"
        )

    @markers.aws.needs_fixing
    def test_create_resource_share(self, snapshot, aws_client, account_id, cleanups):
        # It is tricky to make this test AWS validated because when resource shares are deleted, AWS still returns
        # them in response.

        snapshot.add_transformer(snapshot.transform.key_value("name"))
        snapshot.add_transformer(snapshot.transform.key_value("arn"))
        snapshot.add_transformer(snapshot.transform.key_value("resourceShareArn"))

        # Ensure CreateResourceShare
        response = aws_client.ram.create_resource_share(name="foo")
        rs_arn = response["resourceShare"]["resourceShareArn"]
        snapshot.match("create-resource-share", response)

        # Ensure UpdateResourceShare
        response = aws_client.ram.update_resource_share(resourceShareArn=rs_arn, name="blah")
        snapshot.match("update-resource-share", response)

        # Ensure GetResourceShares
        response = aws_client.ram.get_resource_shares(resourceOwner="SELF")
        snapshot.match("get-resource-shares", response)

        # Create with a permission
        perm_arn = aws_client.ram.create_permission(
            name=short_uid(),
            resourceType="appsync:Apis",
            policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL"}',
        )["permission"]["arn"]
        response = aws_client.ram.create_resource_share(name=short_uid(), permissionArns=[perm_arn])
        rs_arn_2 = response["resourceShare"]["resourceShareArn"]
        cleanups.append(lambda: aws_client.ram.delete_permission(permissionArn=perm_arn))
        cleanups.append(lambda: aws_client.ram.delete_resource_share(resourceShareArn=rs_arn_2))
        snapshot.match("create-resource-share-with-permission", response)

        # Raise if using a non-existent permission
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_resource_share(
                name=short_uid(), permissionArns=[perm_arn + "invalid"]
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == f"The permission {perm_arn + 'invalid'} does not exist."

        # Create with a IAM role principal
        response = aws_client.ram.create_resource_share(
            name=short_uid(), principals=["arn:aws:iam::123456789012:role/rolename"]
        )
        rs_arn_3 = response["resourceShare"]["resourceShareArn"]
        cleanups.append(
            lambda: aws_client.ram.delete_resource_share(
                resourceShareArn=rs_arn_3,
            )
        )
        snapshot.match("create-resource-share-with-iam-role-principal", response)

        # Create with a IAM user principal
        response = aws_client.ram.create_resource_share(
            name=short_uid(), principals=["arn:aws:iam::123456789012:user/username"]
        )
        rs_arn_4 = response["resourceShare"]["resourceShareArn"]
        cleanups.append(
            lambda: aws_client.ram.delete_resource_share(
                resourceShareArn=rs_arn_4,
            )
        )
        snapshot.match("create-resource-share-with-iam-user-principal", response)

        # Create with an account principal
        response = aws_client.ram.create_resource_share(name=short_uid(), principals=[account_id])
        rs_arn_5 = response["resourceShare"]["resourceShareArn"]
        cleanups.append(
            lambda: aws_client.ram.delete_resource_share(
                resourceShareArn=rs_arn_5,
            )
        )
        snapshot.match("create-resource-share-with-account-principal", response)

        # Raise if using a bad principal
        with pytest.raises(ClientError) as exc:
            aws_client.ram.create_resource_share(name=short_uid(), principals=["ftw"])
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == "Principal ID is malformed. Verify the ID and try again."

        # Create with a resource ARN
        example_resource_name = short_uid()
        response = aws_client.appsync.create_graphql_api(
            name=example_resource_name, authenticationType="API_KEY"
        )
        example_resource_arn = response["graphqlApi"]["arn"]
        cleanups.append(lambda: aws_client.appsync.delete_graphql_api(apiId=example_resource_arn))

        response = aws_client.ram.create_resource_share(
            name=short_uid(), resourceArns=[example_resource_arn]
        )
        rs_arn_5 = response["resourceShare"]["resourceShareArn"]
        cleanups.append(
            lambda: aws_client.ram.delete_resource_share(
                resourceShareArn=rs_arn_5,
            )
        )
        snapshot.match("create-resource-share-with-resource-arn", response)

        # Ensure DeleteResourceShare
        response = aws_client.ram.delete_resource_share(resourceShareArn=rs_arn)
        snapshot.match("delete-resource-share", response)

        # Ensure GetResourceShares
        response = aws_client.ram.get_resource_shares(resourceOwner="SELF")
        snapshot.match("get-resource-shares-2", response)

        # Ensure ListResourceSharePermissions
        response = aws_client.ram.list_resource_share_permissions(resourceShareArn=rs_arn_2)
        snapshot.match("list-resource-share-permissions", response)

        # Ensure AssociateResourceShare
        response = aws_client.ram.associate_resource_share(
            resourceShareArn=rs_arn_2,
            principals=["000000112358", "000000224488"],
            resourceArns=[
                "arn:aws:license-manager:us-east-1:999999999999:license-configuration/lic-123"
            ],
        )
        snapshot.match("associate-resource-share", response)

        # Ensure DissociateResourceShare
        response = aws_client.ram.disassociate_resource_share(
            resourceShareArn=rs_arn_2,
            principals=["000000112358"],
            resourceArns=[
                "arn:aws:license-manager:us-east-1:999999999999:license-configuration/lic-123"
            ],
        )
        snapshot.match("disassociate-resource-share", response)

    @markers.aws.validated
    def test_tags(self, snapshot, aws_client, cleanups):
        snapshot.add_transformer(snapshot.transform.key_value("name"))
        snapshot.add_transformer(snapshot.transform.key_value("arn"))

        permission_name = short_uid()
        result = aws_client.ram.create_permission(
            name=permission_name,
            resourceType="appsync:Apis",
            policyTemplate='{"Effect": "Allow", "Action": "appsync:SourceGraphQL"}',
            tags=[{"key": "foo", "value": "bar"}],
        )
        permission_arn = result["permission"]["arn"]
        cleanups.append(lambda: aws_client.ram.delete_permission(permissionArn=permission_arn))

        rs_name = short_uid()
        response = aws_client.ram.create_resource_share(name=rs_name)
        rs_arn = response["resourceShare"]["resourceShareArn"]
        cleanups.append(lambda: aws_client.ram.delete_resource_share(resourceShareArn=rs_arn))

        # Ensure TagResource
        with pytest.raises(ClientError) as exc:
            aws_client.ram.tag_resource(
                resourceArn=permission_arn,
                resourceShareArn=rs_arn,
                tags=[{"key": "service", "value": "spotify"}],
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == "Only one of resourceArn or resourceShareArn may be specified"

        response = aws_client.ram.tag_resource(
            resourceArn=permission_arn, tags=[{"key": "artist", "value": "led zeppelin"}]
        )
        snapshot.match("tag-resource-permission", response)

        response = aws_client.ram.tag_resource(
            resourceShareArn=rs_arn, tags=[{"key": "album", "value": "ii"}]
        )
        snapshot.match("tag-resource-resource-share", response)

        # Ensure UntagResource
        with pytest.raises(ClientError) as exc:
            aws_client.ram.untag_resource(
                resourceArn=permission_arn, resourceShareArn=rs_arn, tagKeys=["service"]
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidParameterException"
        assert err["Message"] == "Only one of resourceArn or resourceShareArn may be specified"

        response = aws_client.ram.untag_resource(
            resourceArn=permission_arn, tagKeys=["artist", "song"]
        )
        snapshot.match("untag-resource-permission", response)

        response = aws_client.ram.untag_resource(resourceShareArn=rs_arn, tagKeys=["album"])
        snapshot.match("untag-resource-resource-share", response)
