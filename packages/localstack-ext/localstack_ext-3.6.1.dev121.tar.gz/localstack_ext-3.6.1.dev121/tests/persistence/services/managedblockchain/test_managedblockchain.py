def test_create_network_node_proposal(persistence_validations, snapshot, aws_client):
    client = aws_client.managedblockchain
    create_network_response = client.create_network(
        Name="OurBlockchainNet",
        Description="OurBlockchainNetDesc",
        Framework="HYPERLEDGER_FABRIC",
        FrameworkVersion="1.2",
        FrameworkConfiguration={"Fabric": {"Edition": "STARTER"}},
        VotingPolicy={
            "ApprovalThresholdPolicy": {
                "ThresholdPercentage": 50,
                "ProposalDurationInHours": 24,
                "ThresholdComparator": "GREATER_THAN",
            }
        },
        MemberConfiguration={
            "Name": "org1",
            "Description": "Org1 first member of network",
            "FrameworkConfiguration": {
                "Fabric": {"AdminUsername": "MyAdminUser", "AdminPassword": "Password123"}
            },
            "LogPublishingConfiguration": {"Fabric": {"CaLogs": {"Cloudwatch": {"Enabled": True}}}},
        },
    )
    network_id = create_network_response["NetworkId"]
    member_id = create_network_response["MemberId"]

    create_node_response = client.create_node(
        NetworkId=network_id,
        MemberId=member_id,
        NodeConfiguration={
            "InstanceType": "bc.t3.small",
            "AvailabilityZone": "us-east-1a",
            "LogPublishingConfiguration": {
                "Fabric": {
                    "ChaincodeLogs": {"Cloudwatch": {"Enabled": True}},
                    "PeerLogs": {"Cloudwatch": {"Enabled": True}},
                }
            },
        },
    )
    node_id = create_node_response["NodeId"]

    def validate():
        snapshot.match(
            "get_node_response",
            client.get_node(NetworkId=network_id, MemberId=member_id, NodeId=node_id),
        )

    persistence_validations.register(validate)
