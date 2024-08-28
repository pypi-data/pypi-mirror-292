import json
import re
import time
from queue import Queue
from typing import Dict
from urllib.parse import urlparse

import pytest
import websockets
from botocore.exceptions import ClientError
from localstack.aws.api.lambda_ import Runtime
from localstack.constants import APPLICATION_JSON, HEADER_CONTENT_TYPE
from localstack.pro.core.services.apigateway.apigateway_utils import get_apigw_invocation_uri
from localstack.pro.core.utils.common import run_coroutine_in_event_loop
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.async_utils import run_sync
from localstack.utils.aws.arns import get_partition
from localstack.utils.collections import select_attributes
from localstack.utils.net import wait_for_port_closed, wait_for_port_open
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry
from localstack.utils.testutil import get_lambda_log_events
from localstack_snapshot.snapshots.transformer import SortingTransformer
from localstack_snapshot.snapshots.transformer_utility import TransformerUtility
from websockets.exceptions import InvalidStatusCode

from tests.aws.services.apigateway.apigateway_fixtures import (
    create_http_authorizer,
    create_http_deployment,
    create_http_integration,
    create_http_route,
    create_http_route_response,
    create_http_stage,
    create_integration_response,
    update_integration_response,
)
from tests.aws.services.apigateway.conftest import (
    LAMBDA_ECHO_EVENT,
    LAMBDA_INT_RESPONSES,
    LAMBDA_MGMT_WS,
    LAMBDA_ROUTES_WS,
    S3_BUCKET_WS_CONNS,
)


def ws_client_retrieve_message(
    url: str, headers: Dict = None, message: str = None, res_queue: Queue = None
):
    """
    Retrieve a message from the WebSocket under the given URL (after optionally sending a message),
    and put the response to a result queue for asynchronous retrieval.
    """
    res_queue = res_queue or Queue()
    headers = headers or {}

    async def start_client(uri):
        if is_aws_cloud():
            hostname = urlparse(uri.replace("wss://", "https://")).hostname
            wait_for_port_open(f"https://{hostname}:443", retries=60, sleep_time=1)
        try:
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                try:
                    if message:
                        await websocket.send(message)
                    result = await websocket.recv()
                except Exception as e:
                    result = e
                await run_sync(res_queue.put, result)
            await websocket.close()
        except Exception as e:
            await run_sync(res_queue.put, e)

    run_coroutine_in_event_loop(start_client(url))
    return res_queue


class TestWebSockets:
    @markers.aws.validated
    def test_apigatewaymanagementapi(self, create_v2_api, aws_client, aws_client_factory, snapshot):
        region = aws_client.apigatewayv2._client.meta.region_name

        snapshot.add_transformer(
            [snapshot.transform.key_value("SourceIp"), snapshot.transform.key_value("UserAgent")]
        )

        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        # create mock integration
        connect_mock_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )

        # create $connect route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="$connect",
            Target=f"integrations/{connect_mock_integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # create $connect route msg
        default_mock_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )

        # create $default route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{default_mock_integration_id}",
        )

        # create $default route msg
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # create integration msg
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=connect_mock_integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="200",
            ResponseTemplates={"200": '{"statusCode": 200}'},
        )

        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=default_mock_integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="200",
            ResponseTemplates={
                "200": '{"statusCode" : 200, "connectionId" : "$context.connectionId"}'
            },
        )

        # deploy WebSocket API
        stage = "dev"
        aws_client.apigatewayv2.create_stage(ApiId=api_id, StageName=stage)
        result = aws_client.apigatewayv2.create_deployment(ApiId=api_id, StageName=stage)
        assert result.get("DeploymentId")

        if is_aws_cloud():
            connection_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"
        else:
            connection_url = f"https://{api_id}.execute-api.localhost.localstack.cloud:4566/{stage}"

        mgmt_client = aws_client_factory(
            region_name=region,
            endpoint_url=connection_url,
        ).apigatewaymanagementapi

        queue = Queue()

        async def ws_client(url):
            # this triggers the $connect route
            async with websockets.connect(url) as websocket:
                await websocket.send('{"action": "message"}')
                ws_msg = await websocket.recv()
                # the response template is used to send the connectionId back to the client
                assert "connectionId" in ws_msg
                # receives connectionId as templated above from response template
                await run_sync(queue.put, json.loads(ws_msg)["connectionId"])

                # little state machine to handle messages coming from apigatewaymanagementapi
                while True:
                    ws_msg = await websocket.recv()
                    action = json.loads(ws_msg)["action"]
                    match action:
                        case "sendmessage":
                            snapshot.match("sendmessage", ws_msg)
                        case _:
                            snapshot.match("action_received", ws_msg)
                            await run_sync(queue.put, ws_msg)

        run_coroutine_in_event_loop(ws_client(endpoint))

        conn_id = queue.get(timeout=5)

        resp = mgmt_client.post_to_connection(
            ConnectionId=conn_id,
            Data=json.dumps({"action": "sendmessage", "data": "test1"}),
        )
        snapshot.match("post_to_connection", resp)

        resp = mgmt_client.get_connection(
            ConnectionId=conn_id,
        )
        snapshot.match("get_connection", resp)

        resp = mgmt_client.delete_connection(
            ConnectionId=conn_id,
        )
        snapshot.match("delete_connection", resp)

        with pytest.raises(ClientError, match="GoneException"):
            mgmt_client.get_connection(ConnectionId=conn_id)

    @markers.aws.validated
    def test_websocket_response_templates(
        self,
        authorizer_lambda_arn,
        apigateway_lambda_integration_role,
        create_v2_api,
        aws_client,
        aws_client_factory,
        snapshot,
    ):
        region = aws_client.apigatewayv2._client.meta.region_name
        snapshot.add_transformer(snapshot.transform.key_value("connectionId"))

        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        kwargs = {
            "Name": f"auth-{short_uid()}",
            "ApiId": api_id,
            "AuthorizerType": "REQUEST",
            "AuthorizerUri": authorizer_lambda_arn,
            "AuthorizerCredentialsArn": apigateway_lambda_integration_role,
            "IdentitySource": ["route.request.header.Authorization"],
        }
        auth_id = create_http_authorizer(aws_client.apigatewayv2, **kwargs)

        # create mock integration
        connect_mock_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )

        # create $connect route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=auth_id,
            RouteKey="$connect",
            Target=f"integrations/{connect_mock_integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # create $default route msg
        default_mock_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )

        # create $default route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{default_mock_integration_id}",
        )

        # create $default route msg
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # create integration msg
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=connect_mock_integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="200",
            ResponseTemplates={"200": '{"statusCode": 200}'},
        )

        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=default_mock_integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="200",
            ResponseTemplates={
                "200": '{"statusCode" : 200, "connectionId" : "$context.connectionId", "principalId" : "$context.authorizer.principalId"}'
            },
        )

        # deploy WebSocket API
        stage = "dev"
        aws_client.apigatewayv2.create_stage(ApiId=api_id, StageName=stage)
        result = aws_client.apigatewayv2.create_deployment(ApiId=api_id, StageName=stage)
        assert result.get("DeploymentId")

        mgmt_client = aws_client_factory(region_name=region).apigatewaymanagementapi
        endpoint = f"{endpoint}/{stage}?QueryString1=queryValue1"
        if is_aws_cloud():
            connection_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"
            mgmt_client = aws_client_factory(
                endpoint_url=connection_url,
                region_name=region,
            ).apigatewaymanagementapi

        queue = Queue()
        # sleep to let the time for the role to be fully active, otherwise the authorization will fail
        if is_aws_cloud():
            time.sleep(30)

        async def ws_client(url, headers):
            # this triggers the $connect route
            async with websockets.connect(url, extra_headers=headers) as websocket:
                # this triggers the $default route
                await websocket.send('{"action": "message"}')
                ws_msg = await websocket.recv()
                # the response template is used to send the connectionId back to the client
                assert "connectionId" in ws_msg
                assert "principalId" in ws_msg
                # receives connectionId as templated above from response template
                await run_sync(queue.put, json.loads(ws_msg)["connectionId"])
                snapshot.match("action_message", ws_msg)

                # little state machine to handle messages coming from apigatewaymanagementapi
                while True:
                    ws_msg = await websocket.recv()
                    action = json.loads(ws_msg)["action"]
                    match action:
                        case "disconnect":
                            await run_sync(queue.put, ws_msg)
                            snapshot.match("action_disconnect", ws_msg)
                            await websocket.close()
                            break
                        case _:
                            snapshot.match("action_received", ws_msg)
                            await run_sync(queue.put, ws_msg)

        run_coroutine_in_event_loop(
            ws_client(
                endpoint, headers={"HeaderAuth1": "headerValue1", "Authorization": "token test123"}
            )
        )

        q_timeout = 10 if is_aws_cloud() else 5
        # get the connection id from the queue and use from now on to send messages, simulate two-way communication
        conn_id = queue.get(timeout=q_timeout)

        # send a "received" message to the client
        response = mgmt_client.post_to_connection(
            ConnectionId=conn_id, Data='{"action": "received"}'
        )
        msg = queue.get(timeout=q_timeout)

        assert msg == '{"action": "received"}'
        snapshot.match("post_to_connection_default", response)

        # send a "disconnect" to the client
        response = mgmt_client.post_to_connection(
            ConnectionId=conn_id, Data='{"action": "disconnect"}'
        )
        msg = queue.get(timeout=q_timeout)

        assert msg == '{"action": "disconnect"}'
        snapshot.match("post_to_connection_disconnect", response)

    @markers.aws.needs_fixing
    @pytest.mark.skip("This test needs a rewrite, as this would not work against AWS")
    def test_websocket_api_with_aws_proxy_integration(
        self,
        create_v2_api,
        apigateway_lambda_integration_role,
        create_lambda_function,
        add_permission_for_integration_lambda,
        aws_client,
    ):
        """
        This test needs a rewrite, as this would not work against AWS.It would need to be separated by integration type
        Also, we would need to fix `create_http_route_response`, as we have 2-ways communication on by default as shown
        by this test.
        """
        queue = Queue()

        bucket = S3_BUCKET_WS_CONNS
        msg = {
            "action": "__echo__",
            "message": {
                "randomProperty": "hello world",
                "randomProperty2": "foo",
                "randomProperty3": "bar",
            },
            "bucket": bucket,
            "id": 0,
        }
        headers = {"h1": "v1", "h2": "v2"}
        auth_token = short_uid()

        async def start_client(uri):
            uri = f"{uri}?authToken={auth_token}"
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                await websocket.send(json.dumps(msg))
                result = await websocket.recv()
                await run_sync(queue.put, json.loads(to_str(result)))

        # create websocket API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        # create lambda integration
        lambda_name = f"lst_test_websocket_{short_uid()}"
        lambda_arn = create_lambda_function(handler_file=LAMBDA_MGMT_WS, func_name=lambda_name)[
            "CreateFunctionResponse"
        ]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=lambda_arn,
            PayloadFormatVersion="1.0",
            CredentialsArn=apigateway_lambda_integration_role,
        )

        # create routes
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
        )

        stage = "dev"
        deployment_id = aws_client.apigatewayv2.create_deployment(ApiId=api_id)["DeploymentId"]
        aws_client.apigatewayv2.create_stage(
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
            RouteSettings={"$connect": {"DetailedMetricsEnabled": True, "LoggingLevel": "DEBUG"}},
        )

        aws_client.s3.create_bucket(Bucket=bucket)

        # start client
        run_coroutine_in_event_loop(start_client(f"{endpoint}/{stage}"))

        # assert that Lambdas have been invoked
        def check_logs():
            logs = get_lambda_log_events(lambda_name, logs_client=aws_client.logs)
            logs_connect = [log for log in logs if "routeKey': '$connect" in log]
            assert len(logs_connect) == 1
            logs_default = [log for log in logs if "routeKey': '$default" in log]
            assert len(logs_default) == 1

        retry(check_logs, retries=5, sleep=1)

        objects = testutil.map_all_s3_objects(
            buckets=[S3_BUCKET_WS_CONNS], to_json=False, s3_client=aws_client.s3
        )
        assert objects
        conn_id = list(objects)[0].split("/conn.")[-1]
        assert conn_id

    @markers.only_on_amd64
    @pytest.mark.parametrize("url_secure", [True, False])
    @pytest.mark.parametrize("handler_error", [False])
    @pytest.mark.parametrize("integration_type", ["HTTP"])
    @markers.aws.needs_fixing
    def test_websocket_api_with_http_integration(
        self, create_websocket_api, url_parser, integration_type, tmp_http_server, aws_client
    ):
        """
        This test needs a rewrite, as this would not work against AWS. It would need to be separated by integration type
        Also, we would need to fix `create_http_route_response`, as we have 2-ways communication on by default as shown
        by this test.
        """
        queue = Queue()
        req_queue = Queue()
        msg = {
            "action": "__echo__",
            "message": {
                "randomProperty": "hello world",
                "randomProperty2": "foo",
                "randomProperty3": "bar",
            },
        }
        headers = {"h1": "v1", "h2": "v2"}
        test_port, invocations = tmp_http_server
        is_http_integration = "HTTP" in integration_type

        num_messages = 4
        auth_token = short_uid()

        async def start_client(uri):
            uri = f"{uri}?q1={auth_token}"
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                while True:
                    i = await run_sync(req_queue.get)
                    if i is None:
                        break
                    msg["id"] = i
                    # second message sent from post_to_connection(..) in Lambda above
                    if i >= 0 and (is_http_integration or i != 1):
                        await websocket.send(json.dumps(msg))
                    if i < 0:
                        await websocket.send(json.dumps({"action": "__one_way_message__"}))
                    result = await websocket.recv()
                    result = result or "{}"
                    await run_sync(queue.put, json.loads(to_str(result)))

        # deploy WebSocket API
        integration_uri = f"http://localhost:{test_port}" if is_http_integration else None
        func_name, api_id, ws_url, int_id = create_websocket_api(integration_type, integration_uri)
        ws_url = url_parser(ws_url)

        # create/update integration
        params = {"integration.request.header.authToken": "route.request.querystring.q1"}
        aws_client.apigatewayv2.update_integration(
            ApiId=api_id, IntegrationId=int_id, RequestParameters=params
        )
        response = aws_client.apigatewayv2.get_integration(ApiId=api_id, IntegrationId=int_id)
        assert response["IntegrationId"] == int_id
        assert response["IntegrationType"] == integration_type
        # create integration response
        rs = aws_client.apigatewayv2.create_integration_response(
            ApiId=api_id, IntegrationId=int_id, IntegrationResponseKey="ik1"
        )
        assert rs["IntegrationResponseKey"] == "ik1"
        int_resp_id = rs["IntegrationResponseId"]

        # start client
        run_coroutine_in_event_loop(start_client(ws_url))
        for i in range(num_messages):
            req_queue.put(i)

        # wait for WebSocket message results
        def check_result():
            if len(received) == num_messages:
                return
            result = queue.get(timeout=0.5)
            # TODO: fix - currently we seem to receive empty payloads from post_to_connection(..)!
            result = result or {"action": "_lambda_"}
            assert result.get("action") in ["__echo__", "_lambda_"]
            received.append(result)
            assert len(received) == num_messages

        received = []
        retry(check_result, retries=20, sleep=0.6)
        assert len(received) == num_messages

        # delete integration response, then send another request
        aws_client.apigatewayv2.delete_integration_response(
            ApiId=api_id, IntegrationId=int_id, IntegrationResponseId=int_resp_id
        )
        req_queue.put(-1)

        def check_result():
            # expecting #messages + "$connect" msg + "__one_way_message__" msg
            assert len(invocations) == num_messages + 2
            invocation_payloads = [json.loads(to_str(inv.data)) for inv in invocations]
            for payload in invocation_payloads:
                assert re.match(r"^[a-zA-Z0-9]+$", payload.get("connId"))
                assert payload.get("body", {}).get("action")

                # ignore messages without a payload
                if (
                    payload.get("body").get("action") != "$connect"
                    and payload.get("body").get("action") != "__one_way_message__"
                ):
                    assert select_attributes(payload.get("payload"), ["randomProperty"]) == {
                        "randomProperty": "hello world"
                    }
                assert payload.get("userAgent")
                # assuming that user-agent is something like "Python/3.8 websockets/9.1" (may
                # change over time)
                assert "websockets" in payload["userAgent"]

        retry(check_result, retries=3, sleep=1)

        # clean up
        aws_client.apigatewayv2.delete_api(ApiId=api_id)
        req_queue.put(None)
        wait_for_port_closed(ws_url, retries=6, sleep_time=0.5)

    @pytest.mark.parametrize("url_secure", [True, False])
    @pytest.mark.parametrize("handler_error", [True])
    @markers.aws.unknown
    def test_websocket_api_reject_connect(self, create_websocket_api, url_parser, aws_client):
        # deploy WebSocket API
        func_name, api_id, url, int_id = create_websocket_api()
        url = url_parser(url)
        res_queue = ws_client_retrieve_message(url)
        result = res_queue.get(timeout=15)
        assert isinstance(result, Exception)

        def check_result():
            # assert that Lambdas have been invoked
            log_group_name = testutil.get_lambda_log_group_name(func_name)
            logs = testutil.list_all_log_events(log_group_name, aws_client.logs)
            assert logs

        retry(check_result, retries=3, sleep=1)

    @markers.aws.unknown
    def test_create_multiple_routes(self, aws_client):
        client = aws_client.apigatewayv2

        # create API
        api_name = f"ws-{short_uid()}"
        response = client.create_api(
            Name=api_name, ProtocolType="WEBSOCKET", RouteSelectionExpression="$request.body.action"
        )
        api_id = response["ApiId"]

        # create integration
        response = client.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationMethod="GET",
            IntegrationUri="http://localhost:1234/api/onconnect",
            PayloadFormatVersion="1.0",
        )
        int_id = response["IntegrationId"]

        # create routes
        route1 = client.create_route(
            ApiId=api_id, RouteKey="$connect", Target=f"integrations/{int_id}"
        )
        route2 = client.create_route(
            ApiId=api_id, RouteKey="$default", Target=f"integrations/{int_id}"
        )

        # create deployment
        response = client.create_deployment(ApiId=api_id)
        deployment_id = response["DeploymentId"]
        response = client.get_deployment(ApiId=api_id, DeploymentId=deployment_id)
        assert response["DeploymentId"] == deployment_id

        # create/update stages
        for stage_name in [short_uid(), "$default"]:
            response = client.create_stage(
                ApiId=api_id, DeploymentId=deployment_id, StageName=stage_name
            )
            assert response["DeploymentId"] == deployment_id
            assert response["StageName"] == stage_name
            response = client.get_stage(ApiId=api_id, StageName=stage_name)
            assert response["DeploymentId"] == deployment_id
            assert response["StageName"] == stage_name
            with pytest.raises(Exception):
                client.get_stage(ApiId=api_id, StageName="invalid_name")
            response = client.update_stage(ApiId=api_id, StageName=stage_name, AutoDeploy=True)
            assert response["AutoDeploy"] is True

        # clean up
        client.delete_route(ApiId=api_id, RouteId=route1["RouteId"])
        client.delete_route(ApiId=api_id, RouteId=route2["RouteId"])
        with pytest.raises(Exception):
            client.delete_route(ApiId=api_id, RouteId=route2["RouteId"])
        client.delete_deployment(ApiId=api_id, DeploymentId=deployment_id)
        with pytest.raises(Exception):
            client.delete_deployment(ApiId=api_id, DeploymentId=deployment_id)
        client.delete_api(ApiId=api_id)

    @markers.aws.unknown
    def test_create_route_responses(self, aws_client):
        client = aws_client.apigatewayv2

        # create API
        api_name = f"ws-{short_uid()}"
        response = client.create_api(
            Name=api_name, ProtocolType="WEBSOCKET", RouteSelectionExpression="$request.body.action"
        )
        api_id = response["ApiId"]

        # create integration
        response = client.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationMethod="GET",
            IntegrationUri="http://localhost:1234/api/onconnect",
            PayloadFormatVersion="1.0",
        )
        int_id = response["IntegrationId"]

        # create routes
        route = client.create_route(
            ApiId=api_id, RouteKey="$connect", Target=f"integrations/{int_id}"
        )
        route_resp = client.create_route_response(
            ApiId=api_id, RouteId=route["RouteId"], RouteResponseKey="k1"
        )
        assert route_resp["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert route_resp["RouteResponseKey"] == "k1"
        resp_id = route_resp["RouteResponseId"]

        # update route response
        response = client.update_route_response(
            ApiId=api_id, RouteId=route["RouteId"], RouteResponseId=resp_id, RouteResponseKey="k2"
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert response["RouteResponseKey"] == "k2"
        response = client.get_route_response(
            ApiId=api_id, RouteId=route["RouteId"], RouteResponseId=resp_id
        )
        assert response["RouteResponseKey"] == "k2"
        assert response["RouteResponseId"] == resp_id

        # create integration response
        int_resp_key = "/400/"
        int_resp = client.create_integration_response(
            ApiId=api_id, IntegrationId=int_id, IntegrationResponseKey=int_resp_key
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        int_resp_id = int_resp["IntegrationResponseId"]

        # list/get integration responses
        responses = client.get_integration_responses(ApiId=api_id, IntegrationId=int_id)
        assert len(responses["Items"]) == 1
        response = client.get_integration_response(
            ApiId=api_id, IntegrationId=int_id, IntegrationResponseId=int_resp_id
        )
        assert response["IntegrationResponseKey"] == int_resp_key

        # update integration response
        response = client.update_integration_response(
            ApiId=api_id,
            IntegrationId=int_id,
            IntegrationResponseId=int_resp_id,
            IntegrationResponseKey="ik2",
        )
        assert response["IntegrationResponseKey"] == "ik2"

        # delete route and integration response
        response = client.delete_route_response(
            ApiId=api_id, RouteId=route["RouteId"], RouteResponseId=resp_id
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 204
        response = client.delete_integration_response(
            ApiId=api_id, IntegrationId=int_id, IntegrationResponseId=int_resp_id
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 204
        with pytest.raises(Exception):
            client.get_integration_response(
                ApiId=api_id, IntegrationId=int_id, IntegrationResponseId=int_resp_id
            )
        with pytest.raises(Exception):
            client.get_route_response(
                ApiId=api_id, RouteId=route["RouteId"], RouteResponseId=resp_id
            )

        # clean up
        client.delete_api(ApiId=api_id)

    @markers.aws.validated
    def test_websocket_non_proxy_response_integration(
        self,
        aws_client,
        apigateway_lambda_integration_role,
        create_lambda_function,
        add_permission_for_integration_lambda,
        account_id,
        snapshot,
    ):
        # create API
        api_name = f"ws-{short_uid()}"
        response = aws_client.apigatewayv2.create_api(
            Name=api_name, ProtocolType="WEBSOCKET", RouteSelectionExpression="$request.body.action"
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        # create mock integration for $connect route
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            RequestTemplates={"default": '{"statusCode": 200}'},
            TemplateSelectionExpression="default",
        )
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )
        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="/200/",
            TemplateSelectionExpression="default",
            ResponseTemplates={"default": '{"statusCode": 200}'},
        )

        # create integration for $default route
        lambda_name = f"lst_test_websocket_{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_INT_RESPONSES, func_name=lambda_name
        )["CreateFunctionResponse"]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=get_apigw_invocation_uri(lambda_arn),
            PayloadFormatVersion="1.0",
            CredentialsArn=apigateway_lambda_integration_role,
            TemplateSelectionExpression="$request.body.value",
            RequestTemplates={
                "A": '{"message": "A"}',
                "B": '{"message": "B"}',
                "C": '{"message": "C"}',
            },
        )

        # create route responses
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
        )
        create_http_route_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteId=route_id,
            RouteResponseKey="$default",  # only allowed value for websockets
        )

        integration_resp = create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="$integration.response.body.errorMessage",
            ResponseTemplates={
                "200": '{"message": "200 OK"}',
                "error message!": '{"message": "400 OK"}',
                "$default": '{"message": "default OK"}',
            },
        )
        integration_resp_id = integration_resp["IntegrationResponseId"]

        # deploy WebSocket API
        stage = "dev"
        deployment_id = create_http_deployment(aws_client.apigatewayv2, ApiId=api_id)
        create_http_stage(
            aws_client.apigatewayv2,
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
            AutoDeploy=True,
        )

        def _connect_and_send_message(m, expected):
            res_queue = ws_client_retrieve_message(
                f"{endpoint}/{stage}",
                message=json.dumps(m),
                headers={HEADER_CONTENT_TYPE: APPLICATION_JSON},
            )

            json_result = res_queue.get(timeout=100)
            assert json_result == expected
            return json.loads(json_result)

        # A - message returns a non error
        # B - message returns error
        tt = {
            "A": json.dumps({"message": "default OK"}),
            "B": json.dumps({"message": "default OK"}),
        }

        # this test how the template selection expression works, or better saying how it doesn't work
        # $integration.response.body.errorMessage is not being used as the template selection expression
        for k, v in tt.items():
            msg = {"value": k}
            result = retry(_connect_and_send_message, retries=15, sleep=1, m=msg, expected=v)
            snapshot.match(f"int_response_error_message_{k}", result)

        update_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseId=integration_resp_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="$integration.response.header.Content-Type",
            ResponseTemplates={
                "application/json": '{"message": "Content-Type is application/json"}',
                "$default": '{"message": "error message!"}',
            },
        )

        # A - message returns a non error
        # B - message returns error
        tt = {
            "A": json.dumps({"message": "Content-Type is application/json"}),
            "B": json.dumps({"message": "Content-Type is application/json"}),
        }

        for k, v in tt.items():
            msg = {"value": k}
            result = retry(_connect_and_send_message, retries=25, sleep=1, m=msg, expected=v)
            snapshot.match(f"int_response_header_{k}", result)

        update_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseId=integration_resp_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="$integration.response.statuscode",
            ResponseTemplates={
                "200": '{"message": "200 OK"}',
                "$default": '{"message": "default message"}',
            },
        )

        # A - message returns a non error
        # B - message returns error
        tt = {
            "A": json.dumps({"message": "200 OK"}),
            "B": json.dumps({"message": "200 OK"}),
        }

        for k, v in tt.items():
            msg = {"value": k}
            result = retry(_connect_and_send_message, retries=25, sleep=1, m=msg, expected=v)
            snapshot.match(f"int_response_key_{k}", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..DomainNameConfigurations..ApiGatewayDomainName",
            "$..DomainNameConfigurations..CertificateArn",
            "$..DomainNameConfigurations..HostedZoneId",
        ]
    )
    def test_create_domain_names(self, aws_client, snapshot, apigw_create_domain):
        client = aws_client.apigatewayv2

        snapshot.add_transformer(
            TransformerUtility.regex(
                r"([A-Za-z0-9]+).localhost.localstack.cloud", "<id>.localhost.localstack.cloud"
            )
        )

        domain = f"{short_uid()}.localhost.localstack.cloud"
        domains_before = client.get_domain_names().get("Items", [])
        response = apigw_create_domain(
            DomainName=domain,
        )
        snapshot.match("create-domain-name", response)

        response = client.get_domain_name(DomainName=domain)
        assert response["DomainName"] == domain
        response = client.get_domain_names()
        assert len(response["Items"]) == len(domains_before) + 1

    @markers.aws.unknown
    def test_create_authorizers(self, aws_client):
        # create API
        api_name = f"ws-{short_uid()}"
        response = aws_client.apigatewayv2.create_api(
            Name=api_name, ProtocolType="HTTP", RouteSelectionExpression="$request.body.action"
        )
        api_id = response["ApiId"]

        auths_before = aws_client.apigatewayv2.get_authorizers(ApiId=api_id).get("Items", [])

        # create authorizer
        name = f"auth-{short_uid()}"
        response = aws_client.apigatewayv2.create_authorizer(
            ApiId=api_id,
            AuthorizerType="REQUEST",
            IdentitySource=["$request.header.Authorization"],
            Name=name,
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 201
        auth_id = response["AuthorizerId"]

        # get authorizer
        response = aws_client.apigatewayv2.get_authorizer(ApiId=api_id, AuthorizerId=auth_id)
        assert response["Name"] == name
        response = aws_client.apigatewayv2.get_authorizers(ApiId=api_id)
        assert len(response["Items"]) == len(auths_before) + 1

        # delete authorizer
        aws_client.apigatewayv2.delete_authorizer(ApiId=api_id, AuthorizerId=auth_id)
        with pytest.raises(Exception):
            aws_client.apigatewayv2.get_authorizer(ApiId=api_id, AuthorizerId=auth_id)

        # clean up
        aws_client.apigatewayv2.delete_api(ApiId=api_id)

    @markers.aws.validated
    def test_ws_connection_with_invalid_auth(
        self,
        apigateway_lambda_integration_role,
        authorizer_lambda_arn,
        create_v2_api,
        snapshot,
        aws_client,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("apiId"))
        snapshot.add_transformer(snapshot.transform.key_value("sourceIp"))
        snapshot.add_transformer(snapshot.transform.key_value("requestId"))
        snapshot.add_transformer(snapshot.transform.key_value("userAgent"))
        snapshot.add_transformer(snapshot.transform.key_value("connectionId"))

        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        kwargs = {
            "Name": f"auth-{short_uid()}",
            "ApiId": api_id,
            "AuthorizerType": "REQUEST",
            "AuthorizerUri": authorizer_lambda_arn,
            "AuthorizerCredentialsArn": apigateway_lambda_integration_role,
            "IdentitySource": ["route.request.header.Authorization"],
        }

        # assert invalid request 1
        with pytest.raises(ClientError) as ctx:
            create_http_authorizer(
                aws_client.apigatewayv2,
                **{**kwargs, "IdentitySource": ["$request.header.Authorization"]},
            )
        snapshot.match("authorizer_error1", ctx.value.response)

        # assert invalid request 2
        with pytest.raises(ClientError) as ctx:
            create_http_authorizer(
                aws_client.apigatewayv2,
                **{
                    **kwargs,
                    "AuthorizerPayloadFormatVersion": "2.0",
                },
            )
        snapshot.match("authorizer_error2", ctx.value.response)

        # assert valid request
        auth_id = create_http_authorizer(aws_client.apigatewayv2, **kwargs)

        # create integration
        template = """{
            "connId": "$context.connectionId",
            "body": $input.body,
            "payload": $util.escapeJavaScript($input.json('$.message')),
            "queryParams": $input.params(),
            "userAgent": "$context.identity.userAgent"
        }"""
        kwargs = {
            "ApiId": api_id,
            "IntegrationType": "MOCK",
            "IntegrationMethod": "POST",
            "RequestTemplates": {APPLICATION_JSON: template},
        }

        # assert invalid request
        with pytest.raises(ClientError) as ctx:
            create_http_integration(
                aws_client.apigatewayv2,
                **{
                    **kwargs,
                    "PayloadFormatVersion": "2.0",
                },
            )
        snapshot.match("integration_error", ctx.value.response)

        # create mock integration for $connect/$disconnect routes
        mock_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )

        # create routes
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=auth_id,
            RouteKey="$connect",
            Target=f"integrations/{mock_integration_id}",
        )
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        with pytest.raises(ClientError) as e:
            create_http_route(
                aws_client.apigatewayv2,
                ApiId=api_id,
                AuthorizationType="CUSTOM",
                AuthorizerId=auth_id,
                RouteKey="$disconnect",
                Target=f"integrations/{mock_integration_id}",
            )
        snapshot.match("authorizer-only-on-connect", e.value.response)

        # create the $default route, otherwise when sending an authorized message, AWS will return 401 Forbidden in the
        # websocket message
        # TODO: create test case with no $default route to see what LS should return
        default_route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{mock_integration_id}",
        )
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=default_route_id, RouteResponseKey="$default"
        )

        # create integration response
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=mock_integration_id,
            IntegrationResponseKey="$default",
            TemplateSelectionExpression="200",
            ResponseTemplates={
                "200": '{"statusCode" : 200, "connectionId" : "$context.connectionId"}'
            },
        )

        # deploy WebSocket API
        stage = "dev"
        aws_client.apigatewayv2.create_stage(ApiId=api_id, StageName=stage)
        result = aws_client.apigatewayv2.create_deployment(ApiId=api_id, StageName=stage)
        assert result.get("DeploymentId")

        # connect to API via WebSocket, assert authentication denied
        headers = {"HeaderAuth1": "headerValue1", "Authorization": "token test123"}
        res_queue = ws_client_retrieve_message(
            f"{endpoint}/{stage}?QueryString1=BOGUS", message="{}", headers=headers
        )
        result = res_queue.get(timeout=40)
        if is_aws_cloud():
            assert isinstance(result, InvalidStatusCode)
            assert result.status_code == 401
        else:
            # TODO: fix parity with real AWS for this error case!
            assert isinstance(result, websockets.ConnectionClosedOK)

        # assert format of Lambda authorizer invocation event
        def _get_lambda_event():
            auth_lambda_name = authorizer_lambda_arn.split(":function:")[-1].split("/")[0]
            logs = get_lambda_log_events(auth_lambda_name, logs_client=aws_client.logs)
            matching = [log for log in logs if "Received event:" in log]
            assert len(matching) == 1
            event = matching[0].partition("Received event:")[2]
            return json.loads(event)

        event = retry(_get_lambda_event, retries=30, sleep=1)
        # snapshot only relevant values
        header_names = ["Authorization", "Connection", "HeaderAuth1", "Upgrade", "User-Agent"]
        event["headers"] = select_attributes(event["headers"], header_names)
        event["multiValueHeaders"] = select_attributes(event["multiValueHeaders"], header_names)
        context_keys = [
            "apiId",
            "eventType",
            "identity",
            "requestId",
            "messageDirection",
            "routeKey",
            "stage",
            "connectionId",
        ]
        event["requestContext"] = select_attributes(event["requestContext"], context_keys)
        event["headers"]["Connection"] = connection = event["headers"]["Connection"].lower()
        event["multiValueHeaders"]["Connection"][0] = connection
        assert re.match(
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
            event["requestContext"]["identity"]["sourceIp"],
        )
        snapshot.match("authorizer_event", event)

        # connect to API with valid authentication credentials
        headers = {"HeaderAuth1": "headerValue1", "Authorization": "token test123"}
        res_queue = ws_client_retrieve_message(
            f"{endpoint}/{stage}?QueryString1=queryValue1",
            message=json.dumps({"action": "message"}),
            headers=headers,
        )
        # xXx: snapshot compare result content (requires full IAM access to Lambda in
        # AWS)
        result = res_queue.get(timeout=20)
        assert '{"statusCode" : 200, "connectionId"' in result

    @markers.aws.validated
    def test_connect_disconnect_always_called(
        self,
        apigateway_lambda_integration_role,
        authorizer_lambda_arn,
        create_v2_api,
        create_lambda_with_invocation_forwarding,
        get_lambda_invocation_events,
        snapshot,
        aws_client,
    ):
        """
        Test to ensure that $connect/$disconnect routes are always invoked (independent of route selection expression)
        """
        snapshot.add_transformer(snapshot.transform.key_value("apiId"))
        snapshot.add_transformer(snapshot.transform.key_value("sourceIp"))
        snapshot.add_transformer(snapshot.transform.key_value("requestId"))
        snapshot.add_transformer(snapshot.transform.key_value("userAgent"))
        snapshot.add_transformer(snapshot.transform.key_value("connectionId"))
        snapshot.add_transformer(snapshot.transform.key_value("connectedAt"))
        snapshot.add_transformer(snapshot.transform.key_value("requestTimeEpoch"))
        snapshot.add_transformer(snapshot.transform.key_value("requestTime"))
        snapshot.add_transformer(SortingTransformer("eventType", lambda o: o["eventType"]))

        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
            ApiKeySelectionExpression="$request.header.x-api-key",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        # create authorizer
        auth_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name=f"auth-{short_uid()}",
            ApiId=api_id,
            AuthorizerType="REQUEST",
            AuthorizerUri=authorizer_lambda_arn,
            AuthorizerCredentialsArn=apigateway_lambda_integration_role,
            IdentitySource=["route.request.header.Authorization"],
        )

        # create integration Lambda function
        lambda_arn = create_lambda_with_invocation_forwarding()

        # create Lambda integration for $connect/$disconnect routes
        lambda_integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=get_apigw_invocation_uri(lambda_arn),
            RequestTemplates={APPLICATION_JSON: '{"context": "$context"}'},
            PayloadFormatVersion="1.0",
        )

        # create routes
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$connect",
            Target=f"integrations/{lambda_integration_id}",
            AuthorizerId=auth_id,
        )
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$disconnect",
            Target=f"integrations/{lambda_integration_id}",
            AuthorizerId=auth_id,
        )
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{lambda_integration_id}",
            AuthorizerId=auth_id,
        )
        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # create integration responses
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=lambda_integration_id,
            IntegrationResponseKey="$default",
        )

        # deploy WebSocket API
        stage = "dev"
        aws_client.apigatewayv2.create_stage(ApiId=api_id, StageName=stage)
        result = aws_client.apigatewayv2.create_deployment(ApiId=api_id, StageName=stage)
        assert result.get("DeploymentId")

        def _parse_dict(ctx_dict_str):
            """Simple workaround function to parse $context strings encoded like '{attr1=v1, attr2=123, ...}'"""
            if not is_aws_cloud():
                return json.loads(ctx_dict_str.replace("'", '"').replace("None", "null"))
            result = {}
            for entry in re.split(r"[,\s]+", ctx_dict_str.strip("{}")):
                key, _, value = entry.partition("=")
                result[key] = value
            return result

        # connect to API and receive invocation messages
        headers = {"x-api-key": "test123", HEADER_CONTENT_TYPE: APPLICATION_JSON}
        res_queue = ws_client_retrieve_message(
            f"{endpoint}/{stage}?q1=v1", message="{}", headers=headers
        )
        result = res_queue.get(timeout=20)
        if is_aws_cloud():
            # TODO: enable!
            result_dict = json.loads(result)
            result_body = json.loads(result_dict["body"])
            snapshot.match("ws-response", _parse_dict(result_body["event"]["context"]))
        # receive and assert invocation messages published to SQS queue by integration Lambda
        messages = get_lambda_invocation_events(lambda_arn, count=3)
        assert len(messages) == 3

        ctx_dicts = []
        event_types = []
        for msg in messages:
            ctx_dict = _parse_dict(msg["event"]["context"])
            event_types.append(ctx_dict["eventType"])
            ctx_dicts.append(ctx_dict)

        assert event_types == ["CONNECT", "MESSAGE", "DISCONNECT"]
        if is_aws_cloud():
            snapshot.match("lambda-events", ctx_dicts)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..EncryptionType", "$..Data"])
    def test_websocket_with_kinesis_integration(
        self,
        create_v2_api,
        create_iam_role_and_attach_policy,
        kinesis_create_stream,
        snapshot,
        aws_client,
    ):
        region = aws_client.apigatewayv2.meta.region_name

        snapshot.add_transformer(snapshot.transform.key_value("SequenceNumber"))
        snapshot.add_transformer(snapshot.transform.key_value("ShardId"))
        snapshot.add_transformer(snapshot.transform.key_value("requestId"))
        snapshot.add_transformer(snapshot.transform.key_value("connectionId"))

        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="\\$default",
            ApiKeySelectionExpression="$request.header.x-api-key",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        stage = "dev"

        # create apigatewayv2 role to call kinesis
        role_arn = create_iam_role_and_attach_policy(
            policy_arn=f"arn:{get_partition(region)}:iam::aws:policy/AmazonKinesisFullAccess",
        )

        # create kinesis stream
        stream_name = f"test-stream-{short_uid()}"
        kinesis_create_stream(StreamName=stream_name, ShardCount=1)

        # create integration
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            CredentialsArn=role_arn,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=f"arn:{get_partition(region)}:apigateway:{region}:kinesis:action/PutRecord",
            RequestTemplates={
                "default": """
                #set($data = "{""body"": $input.body, ""connectionId"":""$context.connectionId""}")
                {
                    "StreamName": "stream_name",
                    "Data": "$util.base64Encode($data)",
                    "PartitionKey": "test-partition"
                }
                """.replace("stream_name", stream_name)
            },
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="/200/",
        )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_http_stage(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)
        create_http_deployment(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)

        def ws_double_quoted_message():
            headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON}
            res_queue = ws_client_retrieve_message(
                url=f"{endpoint}/{stage}", message='{"f": 1}', headers=headers
            )
            json_result = res_queue.get(timeout=40)
            result = json.loads(json_result)
            assert result.get("SequenceNumber", None)
            snapshot.match("kinesis-response-1", json.loads(json_result))

        def ws_random_message():
            headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON}
            res_queue = ws_client_retrieve_message(
                url=f"{endpoint}/{stage}", message="$u{}\\1", headers=headers
            )
            json_result = res_queue.get(timeout=40)
            result = json.loads(json_result)
            assert result.get("SequenceNumber", None)
            snapshot.match("kinesis-response-2", json.loads(json_result))

        retry(ws_double_quoted_message, retries=15, sleep=2)
        retry(ws_random_message, retries=15, sleep=2)

        shard_iterator = aws_client.kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId="shardId-000000000000",
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]

        response = aws_client.kinesis.get_records(ShardIterator=shard_iterator)
        snapshot.match("kinesis-get-records", response["Records"])

        regex = r"(?:\"body\":([^,]+)),\s\"connectionId\":\"((.*))\""
        for record in response["Records"]:
            data = record["Data"]
            data = data.decode("utf-8")
            match = re.search(regex, data)
            body = match[1]
            connection_id = match[2]
            assert body, data
            assert connection_id, data

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..MD5OfMessageAttributes", "$..MD5OfMessageSystemAttributes", "$..SequenceNumber"]
    )
    def test_websocket_with_sqs_integration(
        self,
        create_v2_api,
        create_iam_role_and_attach_policy,
        sqs_create_queue,
        region_name,
        account_id,
        snapshot,
        aws_client,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfMessageBody"))
        snapshot.add_transformer(snapshot.transform.key_value("MessageId"))
        snapshot.add_transformer(snapshot.transform.key_value("RequestId"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(snapshot.transform.key_value("ReceiptHandle"))

        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="\\$default",
            ApiKeySelectionExpression="$request.header.x-api-key",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        stage = "dev"

        # create apigatewayv2 role to call sqs
        role_arn = create_iam_role_and_attach_policy(
            policy_arn=f"arn:{get_partition(region_name)}:iam::aws:policy/AmazonSQSFullAccess"
        )

        queue_name = f"queue{short_uid()}"
        queue_url = sqs_create_queue(QueueName=queue_name)

        # create mock integration for $connect
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            RequestTemplates={"default": '{"statusCode": 200}'},
            TemplateSelectionExpression="default",
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="$default",
            ResponseTemplates={"$default": '{"statusCode": 200}'},
        )

        # create sqs integration for $default
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            CredentialsArn=role_arn,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=f"arn:aws:apigateway:{region_name}:sqs:path/{account_id}/{queue_name}",
            RequestParameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            },
            RequestTemplates={
                "default": "Action=SendMessage&MessageBody=$util.urlEncode($input.body)"
            },
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="$default",
            ResponseTemplates={"$default": "$input.body"},
        )

        # create sqs integration for $disconnect
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            CredentialsArn=role_arn,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=f"arn:aws:apigateway:{region_name}:sqs:path/{account_id}/{queue_name}",
            RequestParameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            },
            RequestTemplates={
                "default": "Action=SendMessage&MessageBody=$util.urlEncode('Client disconnected')"
            },
            PassthroughBehavior="NEVER",
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$disconnect",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_http_stage(aws_client.apigatewayv2, ApiId=api_id, StageName=stage, AutoDeploy=True)

        def _connect_and_send_message_to_sqs():
            res_queue = ws_client_retrieve_message(
                f"{endpoint}/{stage}",
                message="test@message",
                headers={HEADER_CONTENT_TYPE: APPLICATION_JSON},
            )
            json_result = res_queue.get(timeout=2)
            d = json.loads(json_result)
            assert d.get("SendMessageResponse", None)
            return d.get("SendMessageResponse")

        result = retry(_connect_and_send_message_to_sqs, retries=15, sleep=1)
        snapshot.match("sqs-response", result.get("SendMessageResult"))

        # poll message from the sqs queue
        def _poll_message_from_sqs():
            sqs_response = aws_client.sqs.receive_message(
                QueueUrl=queue_url, MaxNumberOfMessages=10
            )
            msgs = sqs_response.get("Messages", None)
            assert len(msgs) > 0
            # check if "Client disconnected" message is present
            for msg in msgs:
                if msg["Body"] == "Client disconnected":
                    return msg

            assert False  # "Client disconnected" message not found

        msg = retry(_poll_message_from_sqs, retries=15, sleep=1)
        snapshot.match("sns-receive-message", msg)

    @markers.aws.validated
    def test_websocket_with_sns_integration(
        self,
        create_v2_api,
        create_iam_role_and_attach_policy,
        sns_create_topic,
        region_name,
        account_id,
        snapshot,
        aws_client,
    ):
        response = create_v2_api(
            ProtocolType="WEBSOCKET", RouteSelectionExpression="$request.body.action"
        )

        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        stage = "dev"

        # create apigatewayv2 role to call sqs
        role_arn = create_iam_role_and_attach_policy(
            policy_arn=f"arn:{get_partition(region_name)}:iam::aws:policy/AmazonSNSFullAccess"
        )

        topic_response = sns_create_topic(Name=f"{short_uid()}")
        topic_arn = topic_response["TopicArn"]

        # create mock integration for $connect
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="MOCK",
            IntegrationMethod="POST",
            RequestTemplates={"200": '{"statusCode": 200}'},
            TemplateSelectionExpression="200",
        )
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
            RouteResponseSelectionExpression="$default",
        )
        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="/200/",
            TemplateSelectionExpression="default",
            ResponseTemplates={
                "200": '{"statusCode": 200, "connectionId": "$context.connectionId"}'
            },
        )

        # create sns integration for $default
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            CredentialsArn=role_arn,
            IntegrationType="AWS",
            IntegrationMethod="POST",
            IntegrationUri=f"arn:aws:apigateway:{region_name}:sns:action/Publish",
            RequestParameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            },
            RequestTemplates={
                "$default": f"Action=Publish&Message=$util.urlEncode($input.json('$'))&TopicArn=$util.urlEncode(\"{topic_arn}\"))"
            },
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
        )
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
        )
        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )
        create_integration_response(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationId=integration_id,
            IntegrationResponseKey="$default",
            ResponseTemplates={"200": '{"statusCode": 200, "message": "order created"}'},
        )

        deployment_id = create_http_deployment(aws_client.apigatewayv2, ApiId=api_id)
        create_http_stage(
            aws_client.apigatewayv2,
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
            AutoDeploy=True,
        )

        def _connect_and_send_message_to_sns():
            res_queue = ws_client_retrieve_message(
                f"{endpoint}/{stage}",
                message="test@message",
                headers={HEADER_CONTENT_TYPE: APPLICATION_JSON},
            )
            json_result = res_queue.get(timeout=2)
            assert json_result == '{"statusCode": 200, "message": "order created"}'
            return json.loads(json_result)

        result = retry(_connect_and_send_message_to_sns, retries=15, sleep=1)
        snapshot.match("sns-response", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..headers",
            "$..args",
            "$..files",
            "$..form",
            "$..json",
            "$..origin",
            "$..url",
            "$..method",
        ]
    )
    @pytest.mark.parametrize("integration_response", (True, False))
    def test_websocket_with_http_proxy_integration(
        self,
        aws_client,
        create_v2_api,
        echo_http_server_post,
        snapshot,
        integration_response,
    ):
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="\\$default",
            ApiKeySelectionExpression="$request.header.x-api-key",
        )

        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        stage = "dev"

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=echo_http_server_post,
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )
        # Integration response is not mandatory for HTTP_PROXY type, test with and without
        if integration_response:
            create_integration_response(
                aws_client.apigatewayv2,
                ApiId=api_id,
                IntegrationId=integration_id,
                IntegrationResponseKey="/200/",
            )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_http_stage(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)
        create_http_deployment(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)

        def ws_random_message():
            headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON}
            res_queue = ws_client_retrieve_message(
                url=f"{endpoint}/{stage}", message='{"foo":"bar"}', headers=headers
            )
            json_result = res_queue.get(timeout=40)
            snapshot.match("ws-http-proxy-response", json.loads(json_result))

        retry(ws_random_message, retries=10, sleep=1)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..integrationLatency"])
    def test_websocket_with_lambda_integration(
        self,
        create_lambda_function,
        apigateway_lambda_integration_role,
        add_permission_for_integration_lambda,
        authorizer_lambda_arn,
        create_v2_api,
        aws_client,
        snapshot,
    ):
        # create API
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        kwargs = {
            "Name": f"auth-{short_uid()}",
            "ApiId": api_id,
            "AuthorizerType": "REQUEST",
            "AuthorizerUri": authorizer_lambda_arn,
            "AuthorizerCredentialsArn": apigateway_lambda_integration_role,
            "IdentitySource": ["route.request.header.Authorization"],
        }
        auth_id = create_http_authorizer(aws_client.apigatewayv2, **kwargs)

        # creates the lambda integration
        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_ECHO_EVENT, func_name=lambda_name, runtime=Runtime.nodejs20_x
        )["CreateFunctionResponse"]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=lambda_arn,
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            CredentialsArn=apigateway_lambda_integration_role,
        )

        # $connect route with authorizer
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=auth_id,
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        stage = "dev"
        deployment_id = aws_client.apigatewayv2.create_deployment(ApiId=api_id)["DeploymentId"]
        aws_client.apigatewayv2.create_stage(
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
            RouteSettings={"$connect": {"DetailedMetricsEnabled": True, "LoggingLevel": "DEBUG"}},
        )

        headers = {"HeaderAuth1": "headerValue1", "Authorization": "token test123"}
        res_queue = ws_client_retrieve_message(
            f"{endpoint}/{stage}?QueryString1=queryValue1", message="{}", headers=headers
        )
        res_queue.get(timeout=20)

        def _get_lambda_event():
            lambda_name = lambda_arn.split(":function:")[-1].split("/")[0]
            logs = get_lambda_log_events(lambda_name, logs_client=aws_client.logs)
            matching = [log for log in logs if "Received event:" in log]
            # assert we only called the authorizer once
            assert len(matching) == 1
            event = matching[0].partition("Received event:")[2]
            return json.loads(event)

        event = retry(_get_lambda_event, retries=10, sleep=1)

        authorizer = event["requestContext"]["authorizer"]
        snapshot.match("authorizer_event", authorizer)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..integrationLatency"])
    def test_websocket_matching_routes(
        self,
        create_lambda_function,
        apigateway_lambda_integration_role,
        add_permission_for_integration_lambda,
        authorizer_lambda_arn,
        create_v2_api,
        aws_client,
    ):
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="$request.body.action",
        )
        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]

        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(handler_file=LAMBDA_ROUTES_WS, func_name=lambda_name)[
            "CreateFunctionResponse"
        ]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=lambda_arn,
            TemplateSelectionExpression="200",
            RequestTemplates={"200": '{"statusCode": 200}'},
            PayloadFormatVersion="1.0",
            CredentialsArn=apigateway_lambda_integration_role,
        )

        # $connect route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="$connect",
            Target=f"integrations/{integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # $default route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        # $disconnect route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="$disconnect",
            Target=f"integrations/{integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        stage = "dev"
        deployment_id = aws_client.apigatewayv2.create_deployment(ApiId=api_id)["DeploymentId"]
        aws_client.apigatewayv2.create_stage(
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
            RouteSettings={"$connect": {"DetailedMetricsEnabled": True, "LoggingLevel": "DEBUG"}},
        )

        env = "local"
        if is_aws_cloud():
            env = "aws"

        # the message doesn't have action so $default route should be used
        res_queue = ws_client_retrieve_message(f"{endpoint}/{stage}", message='{"env": "%s"}' % env)
        res_queue.get(timeout=15)

        def _get_lambda_event():
            lambda_name = lambda_arn.split(":function:")[-1].split("/")[0]
            logs = get_lambda_log_events(lambda_name, logs_client=aws_client.logs)
            matching = [log for log in logs if "Received event:" in log]
            return matching

        events = retry(_get_lambda_event, retries=10, sleep=1)
        for evt in events:
            # extract the route key from string using regex
            pattern = r"'routeKey': '([^']+)'"
            match = re.search(pattern, evt)
            if match:
                assert match.group(1) in ["$connect", "$default", "$disconnect"]
            else:
                assert False

        # foobar route
        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="foobar",
            Target=f"integrations/{integration_id}",
        )

        aws_client.apigatewayv2.create_route_response(
            ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        stage = "stage"
        deployment_id = aws_client.apigatewayv2.create_deployment(ApiId=api_id)["DeploymentId"]
        aws_client.apigatewayv2.create_stage(
            ApiId=api_id,
            StageName=stage,
            DeploymentId=deployment_id,
        )

        res_queue = ws_client_retrieve_message(
            f"{endpoint}/{stage}", message='{"action":"foobar","env": "%s"}' % env
        )
        res_queue.get(timeout=15)

        events = retry(_get_lambda_event, retries=10, sleep=1)
        events = [evt for evt in events if "'stage': 'stage'" in evt]
        assert events

        for evt in events:
            # extract the route key from string using regex
            pattern = r"'routeKey': '([^']+)'"
            match = re.search(pattern, evt)
            if match:
                assert match.group(1) in ["$connect", "foobar", "$disconnect"]
            else:
                assert False

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..headers.Accept",
            "$..headers.Accept-Encoding",
            "$..headers.Connection",
            "$..headers.Content-Type",
            "$..headers.Sec-Websocket-Extensions",
            "$..headers.Sec-Websocket-Key",
            "$..headers.Sec-Websocket-Version",
            "$..headers.Upgrade",
            "$..headers.X-Amzn-Apigateway-Api-Id",
            "$..headers.X-Amzn-Trace-Id",
            "$..headers.Content-Length",  # TODO: content-length is one shorter in AWS (newline?)
            "$..args",
            "$..files",
            "$..form",
            "$..json",
            "$..url",
            "$..origin",
            "$..method",
        ]
    )
    def test_websocket_with_http_proxy_integration_request_parameters(
        self,
        aws_client,
        create_v2_api,
        echo_http_server_post,
        snapshot,
    ):
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("User-Agent"),
                snapshot.transform.key_value("Host"),
                snapshot.transform.key_value("Apiid"),
                snapshot.transform.key_value("X-Amzn-Apigateway-Api-Id"),
                snapshot.transform.key_value("X-Amzn-Trace-Id"),
                snapshot.transform.key_value("Connectionid"),
                snapshot.transform.key_value("origin"),
                snapshot.transform.key_value("url"),
            ]
        )
        response = create_v2_api(
            ProtocolType="WEBSOCKET",
            RouteSelectionExpression="\\$default",
            ApiKeySelectionExpression="$request.header.x-api-key",
        )

        api_id = response["ApiId"]
        endpoint = response["ApiEndpoint"]
        stage = "dev"

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=echo_http_server_post,
            TemplateSelectionExpression="default",
            PayloadFormatVersion="1.0",
            RequestParameters={
                "integration.request.header.connectionId": "context.connectionId",
                "integration.request.header.stageName": "context.stage",
                "integration.request.header.apiId": "context.apiId",
            },
        )

        route_id = create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="$default",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        create_http_route_response(
            aws_client.apigatewayv2, ApiId=api_id, RouteId=route_id, RouteResponseKey="$default"
        )

        create_http_stage(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)
        create_http_deployment(aws_client.apigatewayv2, ApiId=api_id, StageName=stage)

        def ws_random_message():
            headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON}
            res_queue = ws_client_retrieve_message(
                url=f"{endpoint}/{stage}", message='{"foo":"bar"}', headers=headers
            )
            json_result = res_queue.get(timeout=40)
            snapshot.match("ws-http-proxy-response", json.loads(json_result))

        retry(ws_random_message, retries=10, sleep=1)
