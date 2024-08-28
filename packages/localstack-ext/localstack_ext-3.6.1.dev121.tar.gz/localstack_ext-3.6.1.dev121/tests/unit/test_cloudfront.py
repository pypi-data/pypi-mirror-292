from localstack.pro.core.services.cloudfront.provider import (
    Distribution,
    format_distribution_summary,
)

distribution = {
    "Distribution": {
        "Id": "e8fcda09",
        "ARN": "arn:aws:cloudfront::000000000000:distribution/e8fcda09",
        "DomainName": "e8fcda09.cloudfront.localhost.localstack.cloud",
        "DistributionConfig": {
            "CallerReference": "TODO",
            "Origins": {
                "Quantity": 1,
                "Items": [{"Id": "1", "DomainName": "mydomain.example.com"}],
            },
            "DefaultCacheBehavior": {
                "TargetOriginId": "1",
                "TrustedSigners": {"Enabled": False, "Quantity": 0},
                "ViewerProtocolPolicy": "TODO",
                "ForwardedValues": {"QueryString": True, "Cookies": {"Forward": "all"}},
                "MinTTL": 600,
            },
            "Comment": "",
            "Enabled": True,
            "Aliases": {"Quantity": 0, "Items": []},
            "OriginGroups": {"Quantity": 0, "Items": []},
            "CacheBehaviors": {"Quantity": 0, "Items": []},
            "CustomErrorResponses": {"Quantity": 0, "Items": []},
        },
        "LastModifiedTime": "2022-02-13T10:09:59.622Z",
        "Status": "Deployed",
    }
}


class TestCloudFront:
    def test_format_attributes_response(self):
        _distribution = Distribution(params=distribution)
        formatted_distribution = format_distribution_summary(_distribution)
        assert isinstance(formatted_distribution["Origins"]["Items"], list)
        assert "CallerReference" not in formatted_distribution
