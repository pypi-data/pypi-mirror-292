import json

from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.strings import short_uid


class TestSQS:
    @markers.aws.unknown
    def test_create_queues_get_arns(self, aws_client, region_name):
        # create queue
        queue_name = "queue-%s" % short_uid()
        response = aws_client.sqs.create_queue(QueueName=queue_name)
        queue_url = response["QueueUrl"]
        assert f"/{queue_name}" in queue_url

        # get queue attributes
        response = aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )
        queue_arn = response["Attributes"]["QueueArn"]
        assert f":{queue_name}" in queue_arn
        assert f":{region_name}:" in queue_arn

        # clean up
        aws_client.sqs.delete_queue(QueueUrl=queue_url)

    @markers.aws.unknown
    def test_dead_letter_queue(self, aws_client, account_id, region_name):
        queue_name = f"queue-{short_uid()}"
        dlq_name = f"queue-{short_uid()}"

        dlq_info = aws_client.sqs.create_queue(QueueName=dlq_name)
        dlq_arn = arns.sqs_queue_arn(dlq_name, account_id, region_name)

        attributes = {
            "RedrivePolicy": json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": 100})
        }
        queue_info = aws_client.sqs.create_queue(QueueName=queue_name, Attributes=attributes)
        queue_url = queue_info["QueueUrl"]

        attrs = aws_client.sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])
        policy = json.loads(attrs["Attributes"]["RedrivePolicy"])
        assert policy["deadLetterTargetArn"] == arns.sqs_queue_arn(
            dlq_name, account_id, region_name
        )

        # clean up
        aws_client.sqs.delete_queue(QueueUrl=queue_url)
        aws_client.sqs.delete_queue(QueueUrl=dlq_info["QueueUrl"])
