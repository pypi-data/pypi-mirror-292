from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestElasticBeanstalk:
    @markers.aws.unknown
    def test_manage_applications(self, aws_client):
        app_name = "app-%s" % short_uid()
        apps_before = aws_client.elasticbeanstalk.describe_applications(
            ApplicationNames=[app_name]
        ).get("Applications", [])

        # create application
        result = aws_client.elasticbeanstalk.create_application(ApplicationName=app_name)
        assert result["Application"]
        assert result["Application"]["ApplicationName"] == app_name

        # get application
        result = aws_client.elasticbeanstalk.describe_applications(ApplicationNames=[app_name])
        assert result
        applications = result["Applications"]
        assert len(applications) == len(apps_before) + 1
        assert applications[-1]["ApplicationName"] == app_name

        # update application
        new_desc = "desc 2 +&<"
        result = aws_client.elasticbeanstalk.update_application(
            ApplicationName=app_name, Description=new_desc
        )
        assert result["Application"]
        assert result["Application"]["ApplicationName"] == app_name
        assert result["Application"]["Description"] == new_desc

        # delete application
        aws_client.elasticbeanstalk.delete_application(ApplicationName=app_name)
        apps_after = aws_client.elasticbeanstalk.describe_applications(
            ApplicationNames=[app_name]
        ).get("Applications", [])
        assert len(apps_before) == len(apps_after)
        aws_client.elasticbeanstalk.delete_application(ApplicationName=app_name)

    @markers.aws.unknown
    def test_manage_application_versions(self, aws_client):
        # create application
        app_name = "app-%s" % short_uid()
        result = aws_client.elasticbeanstalk.create_application(ApplicationName=app_name)
        assert result
        assert result["Application"]["ApplicationName"] == app_name

        # create application version
        label = "label1"
        result = aws_client.elasticbeanstalk.create_application_version(
            ApplicationName=app_name, VersionLabel=label
        )
        assert result
        assert result.get("ApplicationVersion", {}).get("VersionLabel") == label

        # get application version
        result = aws_client.elasticbeanstalk.describe_application_versions(ApplicationName=app_name)
        assert result
        versions = result["ApplicationVersions"]
        assert versions[-1].get("VersionLabel") == label

        # update application version
        new_desc = "desc 2 +&<"
        result = aws_client.elasticbeanstalk.update_application_version(
            ApplicationName=app_name, VersionLabel=label, Description=new_desc
        )
        assert result
        result = aws_client.elasticbeanstalk.describe_application_versions(ApplicationName=app_name)
        assert result["ApplicationVersions"][-1].get("Description") == new_desc

        # delete application version
        aws_client.elasticbeanstalk.delete_application_version(
            ApplicationName=app_name, VersionLabel=label
        )
        aws_client.elasticbeanstalk.delete_application(ApplicationName=app_name)

    @markers.aws.unknown
    def test_manage_environments(self, aws_client):
        # create application
        app_name = "app-%s" % short_uid()
        aws_client.elasticbeanstalk.create_application(ApplicationName=app_name)

        # create environment
        env_name = "env-%s" % short_uid()
        result = aws_client.elasticbeanstalk.create_environment(
            ApplicationName=app_name, EnvironmentName=env_name
        )
        assert result["EnvironmentName"] == env_name
        assert result.get("EnvironmentId")

        # describe environment
        result = aws_client.elasticbeanstalk.describe_environments(
            ApplicationName=app_name, EnvironmentNames=[env_name]
        )
        assert result
        assert result["Environments"][-1]["EnvironmentName"] == env_name

        # update environment
        result = aws_client.elasticbeanstalk.update_environment(
            ApplicationName=app_name, EnvironmentName=env_name, Description="d2"
        )
        assert result
        result = aws_client.elasticbeanstalk.describe_environments(
            ApplicationName=app_name, EnvironmentNames=[env_name]
        )
        assert result["Environments"][-1]["Description"] == "d2"

        # clean up
        aws_client.elasticbeanstalk.delete_environment_configuration(
            ApplicationName=app_name, EnvironmentName=env_name
        )

        aws_client.elasticbeanstalk.delete_environment_configuration(
            ApplicationName=app_name, EnvironmentName=env_name
        )
        aws_client.elasticbeanstalk.delete_application(ApplicationName=app_name)
