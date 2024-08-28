from localstack.utils.strings import short_uid


def test_get_topic_attributes(persistence_validations, snapshot, aws_client):
    topic_arn = aws_client.sns.create_topic(Name=f"topic-{short_uid()}")["TopicArn"]

    def validate():
        snapshot.match(
            "attributes", aws_client.sns.get_topic_attributes(TopicArn=topic_arn)["Attributes"]
        )

    persistence_validations.register(validate)


def test_sqs_subscription(
    persistence_validations, sqs_get_queue_arn, sns_allow_topic_sqs_queue, aws_client
):
    topic_arn = aws_client.sns.create_topic(Name=f"topic-{short_uid()}")["TopicArn"]
    queue_url = aws_client.sqs.create_queue(QueueName=f"q-{short_uid()}")["QueueUrl"]
    queue_arn = sqs_get_queue_arn(queue_url)

    # connect sns topic to sqs
    aws_client.sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

    # allow topic to write to sqs queue
    sns_allow_topic_sqs_queue(
        sqs_queue_url=queue_url, sqs_queue_arn=queue_arn, sns_topic_arn=topic_arn
    )

    def validate():
        # verify that the subscription still works after restarting localstack
        payload = f"hello world {short_uid()}"
        aws_client.sns.publish(TopicArn=topic_arn, Message=payload)
        response = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=10)

        assert response["Messages"]
        message = response["Messages"][0]
        aws_client.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])

        assert payload in message["Body"]

    persistence_validations.register(validate)


def test_subscription_attributes(persistence_validations, sqs_get_queue_arn, snapshot, aws_client):
    topic_arn = aws_client.sns.create_topic(Name=f"topic-{short_uid()}")["TopicArn"]
    queue_url = aws_client.sqs.create_queue(QueueName=f"q-{short_uid()}")["QueueUrl"]
    queue_arn = sqs_get_queue_arn(queue_url)

    # connect sns topic to sqs
    subscription = aws_client.sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)
    subscription_arn = subscription["SubscriptionArn"]

    def validate():
        snapshot.match(
            "attributes",
            aws_client.sns.get_subscription_attributes(SubscriptionArn=subscription_arn),
        )

    persistence_validations.register(validate)
