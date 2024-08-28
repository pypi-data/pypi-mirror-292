import contextlib
import json

import pytest
from botocore.exceptions import ClientError
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry

TEST_CSV_1 = """
id, name, amount
id1, name1, 123
id2, name2, 234
""".strip()


@pytest.fixture
def glacier_create_vault(aws_client, account_id, aws_client_factory):
    vaults = []

    def _create_vault(glacier_client=None, **kwargs):
        glacier_client = glacier_client or aws_client.glacier
        response = glacier_client.create_vault(**kwargs)
        vaults.append((glacier_client, kwargs["vaultName"]))
        return response

    yield _create_vault

    for client, vault_name in vaults:
        with contextlib.suppress(ClientError):
            client.delete_vault(vaultName=vault_name, accountId=account_id)


class TestGlacier:
    @markers.aws.unknown
    def test_inventory_retrieval(
        self,
        sns_create_topic,
        sqs_create_queue,
        sqs_get_queue_arn,
        sns_subscription,
        aws_client,
        account_id,
        glacier_create_vault,
    ):
        # create vault
        vault_name = f"vault-{short_uid()}"
        glacier_create_vault(vaultName=vault_name)

        # create SNS topic connected to SQS queue
        topic_arn = sns_create_topic()["TopicArn"]
        queue_url = sqs_create_queue()
        queue_arn = sqs_get_queue_arn(queue_url)
        sns_subscription(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

        # initiate inventory retrieval job
        response = aws_client.glacier.initiate_job(
            accountId=account_id,
            vaultName=vault_name,
            jobParameters={
                "Description": "My inventory job",
                "Format": "CSV",
                "SNSTopic": topic_arn,
                "Type": "inventory-retrieval",
            },
        )

        # wait for SNS notification to arrive
        messages = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=10)[
            "Messages"
        ]
        assert messages
        assert "My inventory job" in messages[0]["Body"]

        # get job output
        response = aws_client.glacier.get_job_output(vaultName=vault_name, jobId=response["jobId"])
        result = json.loads(to_str(response["body"].read()))
        assert "ArchiveList" in result

    @markers.aws.needs_fixing
    @markers.snapshot.skip_snapshot_verify(paths=["$..location"])  # wrong format from moto
    def test_select_query_archive(
        self,
        aws_client,
        aws_client_factory,
        snapshot,
        account_id,
        glacier_create_vault,
        s3_bucket,
    ):
        # create the Glacier client somewhere else than us-east-1 for AWS, as often
        # raise `InsufficientCapacityException`
        vault_name = f"vault-{short_uid()}"
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("archiveId"),
                snapshot.transform.key_value("checksum"),
                snapshot.transform.regex(vault_name, "<vault-name>"),
            ]
        )
        if is_aws_cloud():
            glacier_region = "eu-west-1"
            glacier = aws_client_factory(region_name=glacier_region).glacier
        else:
            glacier = aws_client.glacier

        # create vault and output bucket
        response = glacier_create_vault(
            vaultName=vault_name, accountId=account_id, glacier_client=glacier
        )
        snapshot.match("create-vault", response)
        output_bucket = s3_bucket

        # upload archives
        response = glacier.upload_archive(
            accountId=account_id,
            body=TEST_CSV_1,
            vaultName=vault_name,
        )
        snapshot.match("upload-archive", response)
        assert "archiveId" in response
        assert "checksum" in response
        assert "location" in response

        # construct parameters and start job
        output_prefix = "test/job/123"
        job_params = {
            "Type": "select",
            "ArchiveId": response["archiveId"],
            "SelectParameters": {
                "InputSerialization": {"csv": {"FileHeaderInfo": "USE"}},
                "ExpressionType": "SQL",
                "Expression": "SELECT COUNT(*) FROM archive",
                "OutputSerialization": {"csv": {}},
            },
            "OutputLocation": {
                "S3": {
                    "BucketName": output_bucket,
                    "Prefix": output_prefix,
                    "StorageClass": "STANDARD",
                }
            },
            "Tier": "Expedited",
        }
        job = glacier.initiate_job(
            vaultName=vault_name, jobParameters=job_params, accountId=account_id
        )
        # FIXME: cannot run the test in AWS for now, the object would be available after 3 to 5 hours
        # will do it manually later
        # snapshot.match("initiate-select-job", job)
        assert "jobId" in job
        assert "jobOutputPath" in job
        job_id = job["jobId"]

        if is_aws_cloud():
            # FIXME: this is currently broken in LocalStack, because we bypass moto for `select` jobs, so moto cannot
            # find it
            def _get_job_result():
                _response = glacier.describe_job(
                    vaultName=vault_name, accountId=account_id, jobId=job_id
                )
                assert _response["Completed"]
                return _response

            retries = 60
            sleep = 5
            retry(_get_job_result, retries=retries, sleep=sleep)

            response = glacier.get_job_output(
                vaultName=vault_name, accountId=account_id, jobId=job_id
            )
            snapshot.match("get-job-output", response)

        objects = testutil.map_all_s3_objects(
            buckets=[output_bucket], to_json=False, s3_client=aws_client.s3
        )
        result_prefix = "/".join([output_bucket, output_prefix, job_id])
        key = f"{result_prefix}/job.txt"
        assert key in objects
        job_txt = objects.pop(key)
        assert job_id in job_txt
        manifest = objects.pop(f"{result_prefix}/result_manifest.txt")
        file1 = manifest.strip().split("\n")[0].replace("s3://", "")
        result_content = objects.pop(file1)
        expected = "2\n"
        assert result_content == expected

    @markers.aws.unknown
    def test_invalid_vault_name(self, aws_client):
        glacier = aws_client.glacier

        methods = ["add_tags_to_vault", "get_vault_notifications"]
        for method in methods:
            with pytest.raises(Exception) as exc:
                getattr(glacier, method)(vaultName="invalid-name")
            exc.match("ResourceNotFoundException")
