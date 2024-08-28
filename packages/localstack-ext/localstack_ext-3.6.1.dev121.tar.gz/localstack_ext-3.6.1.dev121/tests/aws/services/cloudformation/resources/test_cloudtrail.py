import os

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..HasCustomEventSelectors",
        "$..HasInsightSelectors",
        "$..HomeRegion",
        "$..IsOrganizationTrail",
    ]
)
def test_cloud_trail_deploy(deploy_cfn_template, aws_client, snapshot, s3_create_bucket):
    snapshot.add_transformer(
        snapshot.transform.key_value("CloudTrail", reference_replacement=True),
        priority=-1,
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("S3BucketName", reference_replacement=True),
        priority=-1,
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("CloudTrailArn", reference_replacement=False),
        priority=-1,
    )

    trail_name = f"trail-{short_uid()}"
    bucket = s3_create_bucket()

    deployment = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__),
            "../../../templates/cloudtrail_deploy.yml",
        ),
        parameters={"TrailName": trail_name, "BucketName": bucket},
    )

    response = aws_client.cloudtrail.get_trail(Name=trail_name)
    snapshot.match("get-trail", response["Trail"])

    trail_arn = deployment.outputs["CloudTrailArn"]

    response = aws_client.cloudtrail.list_tags(ResourceIdList=[trail_arn])
    snapshot.match("tags", response["ResourceTagList"])
    snapshot.match("stack_outputs", deployment.outputs)
