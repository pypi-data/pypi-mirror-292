def test_ec2_describe_route_tables(persistence_validations, snapshot, aws_client):
    vpc = aws_client.ec2.create_vpc(CidrBlock="10.0.0.0/16")
    route_table_id = aws_client.ec2.create_route_table(VpcId=vpc["Vpc"]["VpcId"])["RouteTable"][
        "RouteTableId"
    ]

    def validate():
        snapshot.match(
            "describe_route_tables",
            aws_client.ec2.describe_route_tables(RouteTableIds=[route_table_id]),
        )

    persistence_validations.register(validate)
