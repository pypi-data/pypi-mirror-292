import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestAmplifyProvider:
    @pytest.mark.skip
    @markers.aws.unknown
    def test_amplify_two_regions_same_app(self):
        # TODO
        pass

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..app.defaultDomain"])
    def test_create_app(self, amplify_create_app, cleanups, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.key_value("appId"))
        snapshot.add_transformer(snapshot.transform.key_value("name"))

        response = aws_client.amplify.create_app(
            name=f"test-app-{short_uid()}", description="my test app"
        )
        app_id = response["app"]["appId"]
        cleanups.append(lambda: aws_client.amplify.delete_app(appId=app_id))
        snapshot.match("create_amplify_app_response", response)

        # assert basic domain name structure
        assert response["app"]["defaultDomain"].startswith(f"{app_id}.amplifyapp")

    @markers.aws.unknown
    def test_list_apps(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        list_result = aws_client.amplify.list_apps()
        assert list_result["apps"] == []
        amplify_create_app(app_name=app_name)
        list_result = aws_client.amplify.list_apps(maxResults=10)
        assert len(list_result["apps"]) == 1
        assert list_result["apps"][0]["name"] == app_name

    @markers.aws.unknown
    def test_update_app(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        assert app["name"] == app_name

        updated_app_name = "updatedTest"
        update_result = aws_client.amplify.update_app(
            appId=app["appId"], name=updated_app_name
        ).get("app")
        assert update_result["name"] == updated_app_name
        assert update_result["appId"] == app["appId"]
        assert update_result["appArn"] == app["appArn"]

    @markers.aws.unknown
    def test_get_app(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        assert app["name"] == app_name

        get_result = aws_client.amplify.get_app(appId=app["appId"])
        assert app == get_result["app"]

    @markers.aws.unknown
    def test_create_branch(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"

        create_result = aws_client.amplify.create_branch(
            appId=app["appId"], branchName=branch_name
        )["branch"]
        assert create_result["branchName"] == branch_name  # branchName

    @markers.aws.unknown
    def test_list_branches(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"

        list_result = aws_client.amplify.list_branches(appId=app["appId"], maxResults=10)
        assert len(list_result["branches"]) == 0
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)

        list_result = aws_client.amplify.list_branches(appId=app["appId"])
        assert len(list_result["branches"]) == 1
        assert list_result["branches"][0]["branchName"] == branch_name

    @markers.aws.unknown
    def test_get_branch(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"

        create_result = aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)
        get_result = aws_client.amplify.get_branch(appId=app["appId"], branchName=branch_name)
        assert create_result["branch"] == get_result["branch"]

    @markers.aws.unknown
    def test_delete_branch(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"

        create_result = aws_client.amplify.create_branch(
            appId=app["appId"], branchName=branch_name
        )["branch"]
        assert create_result["branchName"] == branch_name  # branchName

        aws_client.amplify.delete_branch(appId=app["appId"], branchName=branch_name)
        list_result = aws_client.amplify.list_branches(appId=app["appId"])
        assert len(list_result["branches"]) == 0

    @markers.aws.unknown
    def test_create_webhook(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)

        create_result = aws_client.amplify.create_webhook(
            appId=app["appId"], branchName=branch_name
        )["webhook"]
        assert "webhookArn" in create_result
        assert "webhookId" in create_result
        assert "webhookUrl" in create_result
        assert create_result["branchName"] == branch_name

    @markers.aws.unknown
    def test_update_webhook(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)

        create_result = aws_client.amplify.create_webhook(
            appId=app["appId"], branchName=branch_name
        )["webhook"]
        webhook_id = create_result["webhookId"]
        new_branch_name = "new_branch"

        aws_client.amplify.create_branch(appId=app["appId"], branchName=new_branch_name)
        update_result = aws_client.amplify.update_webhook(
            webhookId=webhook_id, branchName=new_branch_name
        )
        assert update_result["webhook"]["branchName"] == new_branch_name

    @pytest.mark.skip
    @markers.aws.unknown
    def test_list_webhooks(self, amplify_create_app, aws_client):
        # TODO: not implemented by the RegionBackend setup
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)

        list_result = aws_client.amplify.list_webhooks(appId=app["appId"])["webhooks"]
        assert len(list_result) == 0
        create_result = aws_client.amplify.create_webhook(
            appId=app["appId"], branchName=branch_name
        )
        list_result = aws_client.amplify.list_webhooks(appId=app["appId"])["webhooks"]
        assert len(list_result) == 1
        assert create_result["webhookId"] == list_result["webhookId"]

    @markers.aws.unknown
    def test_get_webhook(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)
        create_result = aws_client.amplify.create_webhook(
            appId=app["appId"], branchName=branch_name
        )["webhook"]
        get_result = aws_client.amplify.get_webhook(webhookId=create_result["webhookId"])["webhook"]
        assert get_result == create_result

    @markers.aws.unknown
    def test_delete_webhook(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        branch_name = "test_branch"
        aws_client.amplify.create_branch(appId=app["appId"], branchName=branch_name)
        create_result = aws_client.amplify.create_webhook(
            appId=app["appId"], branchName=branch_name
        )["webhook"]
        webhook_id = create_result["webhookId"]
        get_result = aws_client.amplify.get_webhook(webhookId=webhook_id)
        assert "webhook" in get_result.keys()
        assert get_result["webhook"]["webhookId"] == webhook_id

        aws_client.amplify.delete_webhook(webhookId=create_result["webhookId"])
        with pytest.raises(Exception) as e:
            aws_client.amplify.get_webhook(webhookId=webhook_id)
        e.match("NotFoundException")

    @markers.aws.unknown
    def test_create_backend_environment(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        environment_name = "test_environment"
        create_result = aws_client.amplify.create_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        assert "backendEnvironmentArn" in create_result["backendEnvironment"]

    @markers.aws.unknown
    def test_get_backend_environment(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        environment_name = "test_environment"
        create_result = aws_client.amplify.create_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        get_result = aws_client.amplify.get_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        assert create_result["backendEnvironment"] == get_result["backendEnvironment"]

    @markers.aws.unknown
    def test_delete_backend_environment(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        app = amplify_create_app(app_name=app_name)
        environment_name = "test_environment"
        create_result = aws_client.amplify.create_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        get_result = aws_client.amplify.get_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        assert get_result["backendEnvironment"] == create_result["backendEnvironment"]

        aws_client.amplify.delete_backend_environment(
            appId=app["appId"], environmentName=environment_name
        )
        with pytest.raises(Exception) as e:
            aws_client.amplify.get_backend_environment(
                appId=app["appId"], environmentName=environment_name
            )
        e.match("NotFoundException")

    @markers.aws.unknown
    def test_tag_untag_resource(self, amplify_create_app, aws_client):
        app_name = f"test-app-{short_uid()}"
        tags = {"tagName1": "tagValue1", "tagName2": "tagValue2"}
        app = amplify_create_app(app_name=app_name)
        app_arn = app["appArn"]
        aws_client.amplify.tag_resource(resourceArn=app_arn, tags=tags)
        list_result = aws_client.amplify.list_tags_for_resource(resourceArn=app_arn)
        assert list_result["tags"] == tags

        tag_keys = list(tags.keys())
        aws_client.amplify.untag_resource(resourceArn=app_arn, tagKeys=tag_keys)
        list_result = aws_client.amplify.list_tags_for_resource(resourceArn=app_arn)
        assert list_result["tags"] == {}

    @markers.aws.validated
    def test_tag_non_existing_app(self, account_id, snapshot, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.amplify.tag_resource(
                resourceArn=f"arn:aws:amplify:us-east-1:{account_id}:apps/doesnotexist",
                tags={"foo": "bar"},
            )
        snapshot.match("tag_app_error", e.value.response)

    @markers.aws.validated
    def test_tag_illegal_resource(self, account_id, snapshot, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.amplify.tag_resource(
                resourceArn=f"arn:aws:amplify:us-east-1:{account_id}:foobared/doesnotexist",
                tags={"foo": "bar"},
            )
        snapshot.match("tag_resource_error", e.value.response)
