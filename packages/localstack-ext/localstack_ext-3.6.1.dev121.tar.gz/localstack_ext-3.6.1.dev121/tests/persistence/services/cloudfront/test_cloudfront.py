import requests
from localstack import config
from localstack.utils.strings import short_uid


def test_cloudfront_s3_origin(persistence_validations, snapshot, aws_client):
    s3_bucket = "cloudfront-bucket"
    aws_client.s3.create_bucket(Bucket=s3_bucket)
    aws_client.s3.put_object(
        Bucket=s3_bucket, Key="index.html", Body=b"<html><body>Hello World!</body></html>"
    )
    aws_client.s3.put_object_acl(ACL="public-read", Bucket=s3_bucket, Key="index.html")

    origin_domain = f"{s3_bucket}.s3.{aws_client.s3.meta.region_name}.amazonaws.com"
    distribution_config = {
        "CallerReference": f"reference-{short_uid()}",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": origin_domain,
                    "DomainName": origin_domain,
                    "S3OriginConfig": {"OriginAccessIdentity": ""},
                }
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": origin_domain,
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {"Forward": "none"},
                "Headers": {"Quantity": 0},
            },
            "ViewerProtocolPolicy": "allow-all",
            "MinTTL": 0,
        },
        "Comment": "some comment",
        "Enabled": True,
    }

    distribution = aws_client.cloudfront.create_distribution(
        DistributionConfig=distribution_config
    )["Distribution"]
    waiter = aws_client.cloudfront.get_waiter("distribution_deployed")
    waiter.wait(Id=distribution["Id"])

    cloudfront_domain = distribution["DomainName"]
    cloudfront_domain += f":{config.GATEWAY_LISTEN[0].port}"
    document_url = f"http://{cloudfront_domain}/index.html"

    def validate():
        snapshot.match(
            "get-distribution", aws_client.cloudfront.get_distribution(Id=distribution["Id"])
        )
        result = requests.get(document_url)
        snapshot.match("distribution-content", result.content)

    persistence_validations.register(validate)
