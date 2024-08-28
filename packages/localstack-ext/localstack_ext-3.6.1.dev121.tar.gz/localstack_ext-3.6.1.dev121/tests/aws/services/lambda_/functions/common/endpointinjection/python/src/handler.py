import boto3

sqs_client = boto3.client("sqs")


def handler(event, context):
    queues = sqs_client.list_queues()
    print("queues=" + str(queues))
    return "ok"
