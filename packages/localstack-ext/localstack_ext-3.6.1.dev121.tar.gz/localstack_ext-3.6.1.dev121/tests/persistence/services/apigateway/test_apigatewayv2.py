from localstack.utils.net import wait_for_port_open
from localstack.utils.strings import short_uid


def test_apigatewayv2_get_client(persistence_validations, snapshot, aws_client):
    api_id = aws_client.apigatewayv2.create_api(ProtocolType="HTTP", Name=f"http-{short_uid()}")[
        "ApiId"
    ]

    # create WebSocket API
    api_endpoint = aws_client.apigatewayv2.create_api(
        ProtocolType="WEBSOCKET",
        Name=f"ws-{short_uid()}",
        RouteSelectionExpression="$request.body.action",
    )["ApiEndpoint"]

    def validate():
        snapshot.match("v2_get_api", aws_client.apigatewayv2.get_api(ApiId=api_id))

        # assert that the endpoint is available (i.e., WebSocket server has been restarted properly)
        port = int(api_endpoint.split(":")[-1])
        wait_for_port_open(port, sleep_time=1, retries=8)

    persistence_validations.register(validate)
