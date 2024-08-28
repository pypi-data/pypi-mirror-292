import json
import logging
import os
import re
import ssl

import aws_cdk as cdk
import pytest
import requests
from botocore.exceptions import ClientError
from localstack import config
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.pro.core.services.cloudfront.provider import get_sample_distribution_config
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.files import load_file
from localstack.utils.ssl import (
    create_ssl_cert,
    get_cert_pem_file_path,
    install_predefined_cert_if_available,
)
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry
from localstack.utils.time import timestamp_millis
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

LOG = logging.getLogger(__name__)

TEST_TEMPLATE = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  TestDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
        - DomainName: test-bucket.s3-eu-west-1.amazonaws.com
          Id: s3ProductionBucket
          S3OriginConfig:
            OriginAccessIdentity: origin-access-identity/cloudfront/E3MPZH9RAHAGMC
        Enabled: 'true'
        Comment: TestDistribution
        DefaultRootObject: index.html
        CustomErrorResponses:
        - ErrorCode: 403
          ResponseCode: 200
          ResponsePagePath: /index.html
        Aliases:
        - example.net
        - www.example.net
        - example.com
        - www.example.com
        DefaultCacheBehavior:
          AllowedMethods:
          - GET
          - HEAD
          Compress: true
          TargetOriginId: s3ProductionBucket
          ForwardedValues:
            QueryString: 'false'
            Cookies:
              Forward: none
          ViewerProtocolPolicy: redirect-to-https
        PriceClass: PriceClass_100
        ViewerCertificate:
          AcmCertificateArn: arn:aws:acm:us-east-1:123456789012:certificate/364912a52-3115-4df9-a067-7290c0a2657s
          MinimumProtocolVersion: TLSv1.1_2016
          SslSupportMethod: sni-only
      Tags:
        - Key: tag1
          Value: value1
"""


@pytest.fixture(scope="session")
def custom_httpserver_with_ssl():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # set SSL context
    # maybe need a serial_number for create_ssl_cert?
    _, cert_file_name, key_file_name = create_ssl_cert()
    context.load_cert_chain(cert_file_name, key_file_name)
    return context


@pytest.fixture(scope="session")
def make_ssl_httpserver(custom_httpserver_with_ssl):
    # we don't want to override SSL for every httpserver fixture
    # see https://pytest-httpserver.readthedocs.io/en/latest/fixtures.html#make-httpserver
    server = HTTPServer(ssl_context=custom_httpserver_with_ssl)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def ssl_httpserver(make_ssl_httpserver):
    server = make_ssl_httpserver
    yield server
    server.clear()


# requesting create_origin_access_control and cleanups fixture here to enforce the distribution deletion
# BEFORE origin access control configs are deleted and the cleanups are executed
@pytest.fixture
def create_distribution(aws_client, create_origin_access_control, cleanups):
    distribution_ids = []

    def _create(**kwargs):
        create_distribution_response = aws_client.cloudfront.create_distribution(**kwargs)
        distribution_ids.append(create_distribution_response["Distribution"]["Id"])
        return create_distribution_response

    yield _create

    # since disabling it and waiting for update takes a lot of time against AWS, but happens in parallel
    # we first disable all, then wait for all, then delete all, instead doing it one by one

    # set all distributions to inactive
    for distribution_id in distribution_ids:
        try:
            get_distribution_config_response = aws_client.cloudfront.get_distribution_config(
                Id=distribution_id
            )
            etag = get_distribution_config_response["ETag"]
            distribution_config = get_distribution_config_response["DistributionConfig"]
            distribution_config["Enabled"] = False
            # update with that (changed) config
            aws_client.cloudfront.update_distribution(
                Id=distribution_id, IfMatch=etag, DistributionConfig=distribution_config
            )
        except Exception as e:
            LOG.debug("Error disabling distribution %s: %s", distribution_id, e)

    # wait for all distributions to be updated
    waiter_config = (
        {"Delay": 30, "MaxAttempts": 60} if is_aws_cloud() else {"Delay": 1, "MaxAttempts": 5}
    )
    waiter = aws_client.cloudfront.get_waiter("distribution_deployed")
    for distribution_id in distribution_ids:
        try:
            waiter.wait(Id=distribution_id, WaiterConfig=waiter_config)
        except Exception as e:
            LOG.debug("Error waiting for distribution %s to be disabled: %s", distribution_id, e)

    # finally delete all distributions
    for distribution_id in distribution_ids:
        try:
            get_distribution_config_response = aws_client.cloudfront.get_distribution_config(
                Id=distribution_id
            )
            etag = get_distribution_config_response["ETag"]
            aws_client.cloudfront.delete_distribution(Id=distribution_id, IfMatch=etag)
        except Exception as e:
            LOG.debug("Error deleting distribution %s: %s", distribution_id, e)


@pytest.fixture
def create_origin_access_control(aws_client):
    origin_access_control_ids = []

    def _create(**kwargs):
        create_origin_access_control_response = aws_client.cloudfront.create_origin_access_control(
            **kwargs
        )
        origin_access_control_ids.append(
            create_origin_access_control_response["OriginAccessControl"]["Id"]
        )
        return create_origin_access_control_response

    yield _create

    # delete all origin access control configs
    for origin_access_control_id in origin_access_control_ids:
        try:
            get_origin_access_control_response = (
                aws_client.cloudfront.get_origin_access_control_config(Id=origin_access_control_id)
            )
            etag = get_origin_access_control_response["ETag"]
            aws_client.cloudfront.delete_origin_access_control(
                Id=origin_access_control_id, IfMatch=etag
            )
        except Exception as e:
            LOG.debug("Error deleting origin access control %s: %s", origin_access_control_id, e)


def get_split_certificate() -> tuple[str, str, str]:
    """
    Splits the installed default certificate into key, cert and chain
    We currently do not split it into cert and chain, which is necessary for ACM however.
    Assumes it is first private key, then cert, then chain in the pem file, which is the case for our LS Let's Encrypt
    certificate

    :return: private_key, certificate, certificate chain
    """
    # setup certificate for alias
    install_predefined_cert_if_available()
    cert_pem_path = get_cert_pem_file_path()
    # split into certificate, chain and key
    pem_file = load_file(cert_pem_path)
    private_key_start = pem_file.index("-----BEGIN PRIVATE KEY-----")
    key_end_marker = "-----END PRIVATE KEY-----"
    private_key_end = pem_file.index(key_end_marker) + len(key_end_marker)
    private_key = pem_file[private_key_start:private_key_end]
    cert_start = pem_file.index("-----BEGIN CERTIFICATE-----")
    cert_end_marker = "-----END CERTIFICATE-----"
    cert_end = pem_file.index(cert_end_marker) + len(cert_end_marker)
    cert = pem_file[cert_start:cert_end]
    # cert end + 1 to avoid leading newline
    cert_chain = pem_file[cert_end + 1 :]
    return private_key, cert, cert_chain


@pytest.mark.skip_store_check(reason="UnsupportedOperation('seek') for CloudFrontStore")
class TestCloudFront:
    @markers.aws.only_localstack
    def test_invoke_distribution(self, aws_client):
        bucket_name = f"test-bucket-{short_uid()}"
        aws_client.s3.create_bucket(Bucket=bucket_name)
        aws_client.s3.put_object(Bucket=bucket_name, Key="index.html", Body=b"test")
        distribution = aws_client.cloudfront.create_distribution(
            DistributionConfig=get_sample_distribution_config(f"{bucket_name}.s3.amazonaws.com")
        )["Distribution"]
        domain = distribution["DomainName"]
        distribution_id = distribution["Id"]
        response = requests.get(f"https://{domain}/index.html")
        assert response.status_code == 200

        # alternative route
        url = f"https://localhost.localstack.cloud/cloudfront/{distribution_id}/index.html"
        response = requests.get(url)
        assert response.status_code == 200

        url = f"http://localhost:4566/cloudfront/{distribution_id}/index.html"
        response = requests.get(url)
        assert response.status_code == 200

    @markers.aws.unknown
    def test_get_distributions(self, aws_client):
        client = aws_client.cloudfront

        # get distributions
        result = client.list_distributions()
        distr_before = result["DistributionList"]["Quantity"]

        # create distribution
        result = client.create_distribution(DistributionConfig=get_sample_distribution_config())
        distr = result["Distribution"]
        assert distr["ARN"].startswith("arn:aws:cloudfront::")

        # assert distribution is contained in list
        result = client.list_distributions()
        distr_after = result["DistributionList"]["Quantity"]
        # TODO: fix assertion, to make tests parallelizable!
        assert distr_after == distr_before + 1

        # clean up
        client.delete_distribution(Id=distr["Id"])

    @markers.aws.unknown
    def test_create_from_cloudformation(self, deploy_cfn_template, aws_client):
        # get distributions
        result = aws_client.cloudfront.list_distributions()
        distr_before = result["DistributionList"]["Quantity"]

        # create stack
        stack = deploy_cfn_template(
            template=TEST_TEMPLATE,
        )
        stack_name = stack.stack_name

        # check created resources
        resources = aws_client.cloudformation.describe_stack_resources(StackName=stack_name)[
            "StackResources"
        ]
        types = set([r.get("ResourceType") for r in resources])
        assert len(types) >= 1

        # assert distribution is contained in list
        result = aws_client.cloudfront.list_distributions()
        distr_after = result["DistributionList"]["Quantity"]
        # TODO: fix assertion, to make tests parallelizable!
        assert distr_after == distr_before + 1
        assert len(result["DistributionList"]["Items"]) == distr_after

    @markers.aws.unknown
    def test_invalidation_waiter(self, aws_client):
        cloudfront = aws_client.cloudfront

        result = cloudfront.create_distribution(DistributionConfig=get_sample_distribution_config())
        distribution_id = result["Distribution"]["Id"]

        invalidation = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": ["/*"]},
                "CallerReference": "test123",
            },
        )["Invalidation"]

        result = cloudfront.get_invalidation(DistributionId=distribution_id, Id=invalidation["Id"])
        assert "Invalidation" in result
        cloudfront.get_waiter("invalidation_completed").wait(
            DistributionId=distribution_id,
            Id=invalidation["Id"],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        cloudfront.delete_distribution(Id=distribution_id)

    @markers.aws.unknown
    def test_create_invalidation(self, aws_client):
        cloudfront = aws_client.cloudfront

        # create distribution
        result = cloudfront.create_distribution(DistributionConfig=get_sample_distribution_config())
        distr_id = result["Distribution"]["Id"]

        # create invalidation
        result = cloudfront.create_invalidation(
            DistributionId=distr_id,
            InvalidationBatch={"Paths": {"Quantity": 0, "Items": []}, "CallerReference": "test123"},
        )
        assert "Invalidation" in result
        inval_id = result["Invalidation"]["Id"]
        with pytest.raises(Exception) as ctx:
            cloudfront.create_invalidation(
                DistributionId="invalid_id",
                InvalidationBatch={
                    "Paths": {"Quantity": 0, "Items": []},
                    "CallerReference": "test123",
                },
            )
        assert "Unable to find" in str(ctx.value)

        # list results
        result = cloudfront.get_invalidation(DistributionId=distr_id, Id=inval_id)
        assert "Invalidation" in result
        result = cloudfront.list_invalidations(DistributionId=distr_id)
        assert result["InvalidationList"]["Quantity"] == 1

        # clean up
        cloudfront.delete_distribution(Id=distr_id)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..FunctionConfig.Comment", "$..Error.Type", "$..ContentType"]
    )
    def test_create_function(self, aws_client, snapshot):
        cloudfront = aws_client.cloudfront
        func_name = "func-%s" % short_uid()

        # create function
        result = cloudfront.create_function(
            Name=func_name,
            FunctionCode=b"code123",
            FunctionConfig={"Comment": "func 1", "Runtime": "cloudfront-js-1.0"},
        )
        func_etag = result["ETag"]
        with pytest.raises(Exception) as ex:
            cloudfront.create_function(
                Name=func_name,
                FunctionCode=b"code123",
                FunctionConfig={"Comment": "func 1", "Runtime": "cloudfront-js-1.0"},
            )
        snapshot.match("already-exists-error", ex.value.response)

        # list/get function
        result = cloudfront.get_function(Name=func_name)
        snapshot.match("get-function-response", result)

        result = cloudfront.list_functions().get("FunctionList", {}).get("Items", [])
        matching = [r for r in result if r.get("Name") == func_name]
        snapshot.match("list-functions-response", matching)

        # update function
        result = cloudfront.update_function(
            Name=func_name,
            IfMatch=func_etag,
            FunctionCode="code456",
            FunctionConfig={"Comment": "comment456", "Runtime": "cloudfront-js-1.0"},
        )
        snapshot.match("update-function-response", result)
        func_etag = result["ETag"]  # etag changes after update

        cloudfront.delete_function(Name=func_name, IfMatch=func_etag)
        with pytest.raises(Exception) as ex:
            cloudfront.get_function(Name=func_name)
        snapshot.match("get-function-not-found-error", ex.value.response)
        snapshot.add_transformer(snapshot.transform.key_value("Name", "function-name"))
        snapshot.add_transformer(snapshot.transform.key_value("ETag", "etag"))

    @markers.aws.unknown
    def test_create_origin_request_policy(self, aws_client):
        policy_name = "policy-%s" % short_uid()

        # create origin request policy
        config = {
            "Comment": "comment1",
            "Name": policy_name,
            "HeadersConfig": {"HeaderBehavior": "none"},
            "CookiesConfig": {"CookieBehavior": "all"},
            "QueryStringsConfig": {"QueryStringBehavior": "all"},
        }
        result = aws_client.cloudfront.create_origin_request_policy(
            OriginRequestPolicyConfig=config
        )
        policy_etag = result["ETag"]
        policy_id = result["OriginRequestPolicy"]["Id"]
        with pytest.raises(Exception) as ctx:
            aws_client.cloudfront.create_origin_request_policy(OriginRequestPolicyConfig=config)
        assert "already exists" in str(ctx.value)

        # list/get origin request policy
        result = aws_client.cloudfront.get_origin_request_policy(Id=policy_id)
        assert "ETag" in result
        assert result["ETag"] == policy_etag
        assert result["OriginRequestPolicy"]["Id"] == policy_id
        result = (
            aws_client.cloudfront.list_origin_request_policies()
            .get("OriginRequestPolicyList", {})
            .get("Items", [])
        )
        matching = [r for r in result if r.get("OriginRequestPolicy", {}).get("Id") == policy_id]
        assert matching
        assert len(matching) == 1

        # update origin request policy
        config["Name"] = "%s-new" % config["Name"]
        config["Comment"] = "comment-new"
        result = aws_client.cloudfront.update_origin_request_policy(
            Id=policy_id, IfMatch=policy_etag, OriginRequestPolicyConfig=config
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        policy = result.get("OriginRequestPolicy", {})
        policy_config = policy.get("OriginRequestPolicyConfig", {})
        assert policy.get("Id") == policy_id
        assert policy_config.get("Name") == config["Name"]
        assert policy_config.get("Comment") == "comment-new"

        # clean up
        aws_client.cloudfront.delete_origin_request_policy(Id=policy_id, IfMatch=policy_etag)
        with pytest.raises(Exception) as ctx:
            aws_client.cloudfront.get_origin_request_policy(Id=policy_id)
        assert "Unable to find" in str(ctx.value)

    @markers.aws.unknown
    def test_create_origin_access_identity(self, aws_client):
        timestamp = timestamp_millis()
        comment = "Test OAI"
        result = aws_client.cloudfront.create_cloud_front_origin_access_identity(
            CloudFrontOriginAccessIdentityConfig={"CallerReference": timestamp, "Comment": comment}
        )

        assert "CloudFrontOriginAccessIdentity" in result
        assert "ETag" in result
        cf_origin_access_identity = result.get("CloudFrontOriginAccessIdentity")
        assert (
            cf_origin_access_identity.get("CloudFrontOriginAccessIdentityConfig", {}).get("Comment")
            == comment
        )
        oai_id = cf_origin_access_identity.get("Id")

        result = aws_client.cloudfront.get_cloud_front_origin_access_identity(Id=oai_id)
        assert result.get("CloudFrontOriginAccessIdentity").get("Id") == oai_id

        result = aws_client.cloudfront.list_cloud_front_origin_access_identities()
        oai_list = result.get("CloudFrontOriginAccessIdentityList")
        assert oai_list
        assert any([i.get("Id") == oai_id for i in oai_list.get("Items")])

        aws_client.cloudfront.delete_cloud_front_origin_access_identity(Id=oai_id)
        aws_client.cloudfront.list_cloud_front_origin_access_identities()

        with pytest.raises(Exception) as ctx:
            aws_client.cloudfront.get_cloud_front_origin_access_identity(Id=oai_id)
        assert "NoSuchCloudFrontOriginAccessIdentity" == ctx.typename

    @pytest.mark.parametrize("static_ports", [True, False])
    @markers.aws.unknown
    def test_custom_errors(self, ssl_httpserver: HTTPServer, static_ports, monkeypatch, aws_client):
        if static_ports:
            from localstack.pro.core import config as ext_config

            monkeypatch.setattr(ext_config, "CLOUDFRONT_STATIC_PORTS", True)

        def _handler(_request: Request) -> Response:
            if _request.path != "/frontend/index.html":
                return Response(b"", status=404)
            response_content = {
                "path": _request.path,
                **payload,
            }
            return Response(json.dumps(response_content), mimetype="application/json", status=200)

        ssl_httpserver.expect_request("").respond_with_handler(_handler)

        payload = {"result": short_uid()}

        # create distribution
        tmpl_path = os.path.join(
            os.path.dirname(__file__), "../../templates", "cloudfront-custom-errors.json"
        )
        distr_config = load_file(tmpl_path).replace(
            "{{local_domain}}", f"{ssl_httpserver.host}:{ssl_httpserver.port}"
        )
        distr_config = json.loads(distr_config)
        result = aws_client.cloudfront.create_distribution(DistributionConfig=distr_config)
        distr = result["Distribution"]
        assert re.match(r"arn:aws[\-a-z]*:cloudfront::.*", distr["ARN"])

        # make test request
        req_path = "/test-non-existing-path"
        if static_ports:
            base_url = f"http://{distr['DomainName']}"
        else:
            base_url = config.internal_service_url(f"{distr['Id']}.cloudfront.{LOCALHOST_HOSTNAME}")
        url = f"{base_url}{req_path}"
        result = requests.get(url)
        assert result
        assert json.loads(to_str(result.content)) == {"path": "/frontend/index.html", **payload}
        first_req, _ = ssl_httpserver.log[0]
        assert first_req.path == f"/frontend{req_path}"
        second_req, _ = ssl_httpserver.log[1]
        assert second_req.path == "/frontend/index.html"

        aws_client.cloudfront.delete_distribution(Id=distr["Id"])

    @markers.aws.unknown
    def test_distribution_with_tags(self, aws_client):
        tags = {"Items": [{"Key": "k1", "Value": "v1"}, {"Key": "k2", "Value": "v2"}]}
        result = aws_client.cloudfront.create_distribution_with_tags(
            DistributionConfigWithTags={
                "DistributionConfig": get_sample_distribution_config(),
                "Tags": tags,
            }
        )
        distribution = result["Distribution"]
        assert distribution["ARN"].startswith("arn:aws:cloudfront::")

        result = aws_client.cloudfront.list_tags_for_resource(Resource=distribution["ARN"])
        tags_result = result.get("Tags", {}).get("Items")
        assert len(tags_result) == 2
        assert tags_result[0].get("Key") == "k1"

        aws_client.cloudfront.untag_resource(
            Resource=distribution["ARN"], TagKeys={"Items": ["k1"]}
        )

        result = aws_client.cloudfront.list_tags_for_resource(Resource=distribution["ARN"])
        tags_result = result.get("Tags", {}).get("Items")
        assert len(tags_result) == 1
        assert tags_result[0].get("Key") == "k2"

        # clean up
        aws_client.cloudfront.delete_distribution(Id=distribution["Id"])

    @markers.aws.unknown
    def test_update_distribution(self, cloudfront_create_distribution, aws_client):
        create_result = cloudfront_create_distribution(
            DistributionConfig=get_sample_distribution_config()
        )
        update_distribution_config = {
            "CallerReference": "TODO Updated",
            "Origins": {"Quantity": 1, "Items": [{"Id": "1", "DomainName": "updated.example.com"}]},
            "DefaultCacheBehavior": {
                "TargetOriginId": "1",
                "ForwardedValues": {"Cookies": {"Forward": "all"}, "QueryString": True},
                "TrustedSigners": {"Quantity": 0, "Enabled": False},
                "ViewerProtocolPolicy": "TODO",
                "MinTTL": 600,
            },
            "Comment": "Updated",
            "Enabled": True,
        }
        aws_client.cloudfront.update_distribution(
            Id=create_result["Distribution"]["Id"], DistributionConfig=update_distribution_config
        )
        updated_distribution_response = aws_client.cloudfront.get_distribution(
            Id=create_result["Distribution"]["Id"]
        )
        updated_distribution = updated_distribution_response["Distribution"]
        updated_distribution_config = updated_distribution["DistributionConfig"]

        assert updated_distribution_config["CallerReference"] == "TODO Updated"
        assert updated_distribution_config["Comment"] == "Updated"
        assert (
            updated_distribution_config["Origins"]["Items"][0]["DomainName"]
            == "updated.example.com"
        )

    @markers.aws.validated
    def test_lambda_redirect(self, deploy_cfn_template, aws_client):
        template_path = os.path.join(
            os.path.dirname(__file__), "../../templates/cloudfront_lambda_redirect.yaml"
        )
        assert os.path.isfile(template_path), f"{template_path} does not exist"

        if is_aws_cloud():
            region_name = aws_client.cloudformation._client_config.region_name
            origin_domain = f"execute-api.{region_name}.amazonaws.com"
        else:
            origin_domain = "execute-api.localhost.localstack.cloud:4566"

        stack = deploy_cfn_template(
            template_path=template_path,
            parameters={
                "OriginDomain": origin_domain,
            },
            max_wait=300,
        )

        host = stack.outputs["CloudfrontHost"]
        if is_aws_cloud():
            url = f"https://{host}/test"
            r = requests.post(url, allow_redirects=False, timeout=(5, 30))
        else:
            # DNS is not set up for tests, so work around the lack of DNS by making a request to
            # localhost with the expected Host header.
            url = f"{config.internal_service_url()}/test"
            r = requests.post(url, headers={"Host": host}, allow_redirects=False, timeout=(5, 30))

        r.raise_for_status()

        assert r.status_code == 302

    @markers.aws.validated
    def test_origin_access_control(self, snapshot, aws_client):
        cloudfront_client = aws_client.cloudfront
        snapshot.add_transformer(snapshot.transform.key_value("Location", "location"))
        snapshot.add_transformer(snapshot.transform.key_value("Id", "id"))
        snapshot.add_transformer(snapshot.transform.key_value("Name", "config-name"))
        snapshot.add_transformer(snapshot.transform.key_value("ETag", "etag"))
        config = {
            "Name": f"control-config-{short_uid()}",
            "Description": "description",
            "OriginAccessControlOriginType": "s3",
            "SigningBehavior": "always",
            "SigningProtocol": "sigv4",
        }

        create_response = cloudfront_client.create_origin_access_control(
            OriginAccessControlConfig=config
        )
        snapshot.match("create_response", create_response)

        control_id = create_response["OriginAccessControl"]["Id"]
        get_response = cloudfront_client.get_origin_access_control(Id=control_id)
        snapshot.match("get_response", get_response)

        etag = create_response["ETag"]
        config["SigningBehavior"] = "never"
        update_response = cloudfront_client.update_origin_access_control(
            Id=control_id, OriginAccessControlConfig=config, IfMatch=etag
        )
        snapshot.match("update_response", update_response)

        get_config_response = cloudfront_client.get_origin_access_control_config(Id=control_id)
        snapshot.match("get_config_response", get_config_response)

        etag = update_response["ETag"]
        delete_response = cloudfront_client.delete_origin_access_control(
            Id=control_id, IfMatch=etag
        )
        snapshot.match("delete_response", delete_response)

    @markers.aws.validated
    # TODO: apparently exception error messages are not rendered 100% correctly
    @markers.snapshot.skip_snapshot_verify(paths=["$..ETag", "$..Error.Message", "$..Message"])
    def test_create_response_headers_policy(self, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.key_value("Location", "location"))
        snapshot.add_transformer(snapshot.transform.key_value("Id", "id"))
        snapshot.add_transformer(snapshot.transform.key_value("Name", "config-name"))
        snapshot.add_transformer(snapshot.transform.key_value("ETag", "etag"))
        cloudfront_client = aws_client.cloudfront

        policy_name = f"pol-{short_uid()}"

        with pytest.raises(ClientError) as exc:
            cloudfront_client.create_response_headers_policy(
                ResponseHeadersPolicyConfig={"Name": policy_name}
            )
        snapshot.match("error-empty", exc.value.response)

        # create policy
        response = cloudfront_client.create_response_headers_policy(
            ResponseHeadersPolicyConfig={
                "Name": policy_name,
                "CustomHeadersConfig": {
                    "Quantity": 1,
                    "Items": [
                        {"Header": "test-header", "Value": "test 123 foobar", "Override": True}
                    ],
                },
            }
        )
        snapshot.match("create-policy-response", response)
        policy_id = response["ResponseHeadersPolicy"]["Id"]
        policy_etag = response["ETag"]

        # get policy
        response = cloudfront_client.get_response_headers_policy(Id=policy_id)
        snapshot.match("get-policy-response", response)

        # update policy
        response = cloudfront_client.update_response_headers_policy(
            Id=policy_id,
            IfMatch=policy_etag,
            ResponseHeadersPolicyConfig={
                "Name": policy_name,
                "CustomHeadersConfig": {
                    "Quantity": 1,
                    "Items": [
                        {"Header": "test-header", "Value": "test 123 updated", "Override": True}
                    ],
                },
            },
        )
        policy_etag = response["ETag"]
        snapshot.match("update-policy-response", response)

        # list policies
        response = cloudfront_client.list_response_headers_policies()
        policies = response["ResponseHeadersPolicyList"]["Items"]
        matching = [
            pol
            for pol in policies
            if pol["ResponseHeadersPolicy"]["ResponseHeadersPolicyConfig"]["Name"] == policy_name
        ]
        snapshot.match("list-policies-response", matching)

        # delete policy
        def _delete_policy():
            response = cloudfront_client.delete_response_headers_policy(
                Id=policy_id,
                IfMatch=policy_etag,
            )
            snapshot.match("delete-policy-response", response)

        retry(_delete_policy, retries=20, sleep=5)

        with pytest.raises(ClientError) as exc:
            cloudfront_client.get_response_headers_policy(Id=policy_id)
        snapshot.match("error-non-existing", exc.value.response)

    @markers.aws.validated
    def test_cloudflare_cname_reuse(
        self, aws_client, aws_client_factory, s3_bucket, create_distribution, snapshot, cleanups
    ):
        caller_reference_1 = f"ref-{short_uid()}"
        caller_reference_2 = f"ref-{short_uid()}"
        origin_domain_name = f"{s3_bucket}.s3.{aws_client.s3.meta.region_name}.amazonaws.com"
        alias_domain = f"{short_uid()}.localhost.localstack.cloud"
        private_key, cert, cert_chain = get_split_certificate()
        acm_client = aws_client_factory(region_name="us-east-1").acm
        import_certificate_result = acm_client.import_certificate(
            Certificate=cert, PrivateKey=private_key, CertificateChain=cert_chain
        )
        cert_arn = import_certificate_result["CertificateArn"]
        cleanups.append(lambda: acm_client.delete_certificate(CertificateArn=cert_arn))

        create_distribution(
            DistributionConfig={
                "CallerReference": caller_reference_1,
                "Origins": {
                    "Quantity": 1,
                    "Items": [
                        {
                            "Id": origin_domain_name,
                            "DomainName": origin_domain_name,
                            "S3OriginConfig": {"OriginAccessIdentity": ""},
                        }
                    ],
                },
                "DefaultCacheBehavior": {
                    "TargetOriginId": origin_domain_name,
                    "ViewerProtocolPolicy": "allow-all",
                    "ForwardedValues": {"Cookies": {"Forward": "all"}, "QueryString": True},
                    "MinTTL": 0,
                },
                "Aliases": {"Quantity": 1, "Items": [alias_domain]},
                "ViewerCertificate": {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                },
                "Comment": "Test distribution",
                "Enabled": True,
            }
        )

        with pytest.raises(ClientError) as e:
            create_distribution(
                DistributionConfig={
                    "CallerReference": caller_reference_2,
                    "Origins": {
                        "Quantity": 1,
                        "Items": [
                            {
                                "Id": origin_domain_name,
                                "DomainName": origin_domain_name,
                                "S3OriginConfig": {"OriginAccessIdentity": ""},
                            }
                        ],
                    },
                    "DefaultCacheBehavior": {
                        "TargetOriginId": origin_domain_name,
                        "ViewerProtocolPolicy": "allow-all",
                        "ForwardedValues": {"Cookies": {"Forward": "all"}, "QueryString": True},
                        "MinTTL": 0,
                    },
                    "Aliases": {"Quantity": 1, "Items": [alias_domain]},
                    "ViewerCertificate": {
                        "ACMCertificateArn": cert_arn,
                        "SSLSupportMethod": "sni-only",
                        "MinimumProtocolVersion": "TLSv1.2_2021",
                    },
                    "Comment": "Test distribution",
                    "Enabled": True,
                }
            )
        snapshot.match("duplicated-alias-exception", e.value.response)

    @markers.aws.validated
    def test_cloudflare_alias_with_s3_backend(
        self,
        aws_client,
        aws_client_factory,
        s3_bucket,
        create_distribution,
        create_origin_access_control,
        cleanups,
    ):
        caller_reference = f"ref-{short_uid()}"
        aws_client.s3.put_object(
            Bucket=s3_bucket, Key="index.html", Body=b"<html><body>test</body></html>"
        )
        origin_domain_name = f"{s3_bucket}.s3.{aws_client.s3.meta.region_name}.amazonaws.com"
        alias_domain = f"{short_uid()}.localhost.localstack.cloud"
        private_key, cert, cert_chain = get_split_certificate()
        acm_client = aws_client_factory(region_name="us-east-1").acm
        import_certificate_result = acm_client.import_certificate(
            Certificate=cert, PrivateKey=private_key, CertificateChain=cert_chain
        )
        cert_arn = import_certificate_result["CertificateArn"]
        cleanups.append(lambda: acm_client.delete_certificate(CertificateArn=cert_arn))

        create_distribution_response = create_distribution(
            DistributionConfig={
                "CallerReference": caller_reference,
                "Origins": {
                    "Quantity": 1,
                    "Items": [
                        {
                            "Id": origin_domain_name,
                            "DomainName": origin_domain_name,
                            "S3OriginConfig": {"OriginAccessIdentity": ""},
                        }
                    ],
                },
                "DefaultCacheBehavior": {
                    "TargetOriginId": origin_domain_name,
                    "ViewerProtocolPolicy": "allow-all",
                    "ForwardedValues": {"Cookies": {"Forward": "all"}, "QueryString": True},
                    "MinTTL": 0,
                },
                "Aliases": {"Quantity": 1, "Items": [alias_domain]},
                "ViewerCertificate": {
                    "ACMCertificateArn": cert_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                },
                "Comment": "Test distribution",
                "Enabled": True,
            }
        )
        distribution_id = create_distribution_response["Distribution"]["Id"]
        distribution_arn = create_distribution_response["Distribution"]["ARN"]
        distribution_domain_name = create_distribution_response["Distribution"]["DomainName"]

        s3_policy = {
            "Version": "2008-10-17",
            "Id": "PolicyForCloudFrontPrivateContent",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudfront.amazonaws.com"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{s3_bucket}/*",
                    "Condition": {"StringEquals": {"AWS:SourceArn": distribution_arn}},
                }
            ],
        }
        aws_client.s3.put_bucket_policy(Bucket=s3_bucket, Policy=json.dumps(s3_policy))

        create_origin_access_control_response = create_origin_access_control(
            OriginAccessControlConfig={
                "Name": origin_domain_name,
                "SigningProtocol": "sigv4",
                "SigningBehavior": "always",
                "OriginAccessControlOriginType": "s3",
            }
        )
        origin_access_control_id = create_origin_access_control_response["OriginAccessControl"][
            "Id"
        ]

        # get current distribution config
        get_distribution_config_response = aws_client.cloudfront.get_distribution_config(
            Id=distribution_id
        )
        etag = get_distribution_config_response["ETag"]
        distribution_config = get_distribution_config_response["DistributionConfig"]
        distribution_config["Origins"]["Items"][0]["OriginAccessControlId"] = (
            origin_access_control_id
        )
        # update with that (changed) config
        aws_client.cloudfront.update_distribution(
            Id=distribution_id, IfMatch=etag, DistributionConfig=distribution_config
        )

        # wait for distribution to be deployed
        waiter = aws_client.cloudfront.get_waiter("distribution_deployed")
        waiter_config = (
            {"Delay": 30, "MaxAttempts": 60} if is_aws_cloud() else {"Delay": 1, "MaxAttempts": 5}
        )
        waiter.wait(Id=distribution_id, WaiterConfig=waiter_config)

        if not is_aws_cloud():
            # we need to alter the port to hit the LS gateway
            distribution_domain_name += f":{config.GATEWAY_LISTEN[0].port}"

        distribution_response = requests.get(
            url=f"http://{distribution_domain_name}/index.html"
        ).content
        alias_response = requests.get(
            url=f"http://{distribution_domain_name}/index.html", headers={"Host": alias_domain}
        ).content
        assert distribution_response == alias_response


class TestCloudFrontRestApiOrigin:
    STACK_NAME = "CloudFrontRestApiOriginStack"

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="CloudFrontRestApiOrigin", force_synth=False)
        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)

        api = cdk.aws_apigateway.RestApi(stack, "test-api", rest_api_name="test-api")

        # Define the Lambda function
        lambda_handler = cdk.aws_lambda.Function(
            stack,
            "lambda-handler",
            runtime=cdk.aws_lambda.Runtime.NODEJS_20_X,
            handler="index.handler",
            code=cdk.aws_lambda.Code.from_inline(
                "exports.handler = async (event) => ({statusCode: 200, body: JSON.stringify(event, null, 4) })"
            ),
        )
        # Integrate Lambda with API Gateway
        api.root.add_method("GET", cdk.aws_apigateway.LambdaIntegration(lambda_handler))

        # Define the CloudFront Distribution
        cloudfront = cdk.aws_cloudfront.Distribution(
            stack,
            "ApiCloudfront",
            default_behavior=cdk.aws_cloudfront.BehaviorOptions(
                origin=cdk.aws_cloudfront_origins.RestApiOrigin(api),
                allowed_methods=cdk.aws_cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cdk.aws_cloudfront.CachePolicy.CACHING_DISABLED,
                origin_request_policy=cdk.aws_cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                viewer_protocol_policy=cdk.aws_cloudfront.ViewerProtocolPolicy.ALLOW_ALL,
            ),
        )

        cdk.CfnOutput(stack, "CloudFrontURL", value=cloudfront.domain_name)
        cdk.CfnOutput(stack, "DistributionId", value=cloudfront.distribution_id)
        cdk.CfnOutput(stack, "ApiId", value=api.rest_api_id)
        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @pytest.fixture
    def cloudfront_url(self, infrastructure):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        distribution_domain_name = outputs["CloudFrontURL"]

        if not is_aws_cloud():
            distribution_domain_name += f":{config.GATEWAY_LISTEN[0].port}"

        return f"https://{distribution_domain_name}/"

    @markers.aws.validated
    def test_auth_headers_and_non_title_case_of_headers(self, cloudfront_url, snapshot):
        headers = {
            "foo": "bar",  # the following two should pass through
            "foo-bar": "baz",
            "authorization": "Bearer ILoveLocalStack1!",  # this should be capitalized
        }
        response = requests.get(cloudfront_url, headers=headers, timeout=(5, 30))
        lambda_event = response.json()
        headers = {
            k: v
            for k, v in lambda_event["headers"].items()
            if k in ["foo", "foo-bar", "Authorization"]
        }
        snapshot.match("headers", headers)

    @markers.aws.validated
    def test_query_string_parameters_forward(self, aws_client, cloudfront_url, snapshot):
        query_string_params = {
            "foo": "bar",
        }
        response = requests.get(cloudfront_url, params=query_string_params, timeout=(5, 30))
        lambda_event = response.json()
        snapshot.match("query-string-parameters", lambda_event["queryStringParameters"])
