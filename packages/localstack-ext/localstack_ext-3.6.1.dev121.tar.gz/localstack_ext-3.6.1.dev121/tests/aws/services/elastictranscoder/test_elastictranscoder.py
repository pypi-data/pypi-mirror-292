import json

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestElasticTranscoder:
    @markers.snapshot.skip_snapshot_verify(paths=["$..Warnings"])
    @markers.aws.validated
    def test_create_list_read_pipeline(self, aws_client, snapshot, s3_create_bucket):
        client = aws_client.elastictranscoder
        iam_client = aws_client.iam
        unique_id = short_uid()
        role_name = f"ElasticTranscoderRole-{unique_id}"
        input_bucket = f"inputbucket-{unique_id}"
        output_bucket = f"outputbucket-{unique_id}"
        pipeline_name = f"Pipeline-{unique_id}"
        snapshot.add_transformer(snapshot.transform.regex(pipeline_name, "<pipeline-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(snapshot.transform.regex(input_bucket, "<input-bucket>"))
        snapshot.add_transformer(snapshot.transform.regex(output_bucket, "<output-bucket>"))

        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "elastictranscoder.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        iam_client.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
        )

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "elastictranscoder:CreatePipeline",
                        "s3:*",
                        "elastictranscoder:DeletePipeline",
                    ],
                    "Resource": "*",
                }
            ],
        }

        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=f"ElasticTranscoderPermissions-{unique_id}",
            PolicyDocument=json.dumps(policy_document),
        )

        s3_create_bucket(Bucket=input_bucket)
        s3_create_bucket(Bucket=output_bucket)
        role = iam_client.get_role(RoleName=role_name)

        create_pipeline = client.create_pipeline(
            Name=pipeline_name,
            InputBucket=input_bucket,
            OutputBucket=output_bucket,
            Role=role["Role"]["Arn"],
        )

        snapshot.match("create_pipeline", create_pipeline)

        pipeline_id = create_pipeline["Pipeline"]["Id"]
        snapshot.add_transformer(snapshot.transform.regex(pipeline_id, "<pipeline-id>"))

        list_pipelines = client.list_pipelines()
        snapshot.match("list_pipelines", list_pipelines)

        read_pipeline = client.read_pipeline(Id=pipeline_id)
        snapshot.match("read_pipeline", read_pipeline)

        # delete pipeline
        client.delete_pipeline(Id=pipeline_id)
        assert not any(
            pipeline["Id"] == pipeline_id for pipeline in client.list_pipelines()["Pipelines"]
        )
