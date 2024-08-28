import pytest
from localstack.pro.core.aws.api.iotwireless import (
    WirelessDeviceIdType,
    WirelessDeviceType,
    WirelessGatewayIdType,
)
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestIotWireless:
    @markers.aws.unknown
    def test_wireless_devices(self, aws_client):
        wireless_device_name = f"wd-{short_uid()}"
        destination_name = f"dest-{short_uid()}"

        devices_before_count = len(
            aws_client.iotwireless.list_wireless_devices()["WirelessDeviceList"]
        )
        result = aws_client.iotwireless.create_wireless_device(
            Name=wireless_device_name,
            Type=WirelessDeviceType.Sidewalk,
            DestinationName=destination_name,
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert "Id" in result
        device_id = result["Id"]

        # list wireless_device
        result = aws_client.iotwireless.list_wireless_devices()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["WirelessDeviceList"]) == devices_before_count + 1

        # get wireless_device
        result = aws_client.iotwireless.get_wireless_device(
            Identifier=device_id,
            IdentifierType=WirelessDeviceIdType.WirelessDeviceId,
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["Name"] == wireless_device_name

        # delete wireless_device
        result = aws_client.iotwireless.delete_wireless_device(Id=device_id)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotwireless.exceptions.ResourceNotFoundException):
            aws_client.iotwireless.get_wireless_device(
                Identifier=device_id,
                IdentifierType=WirelessDeviceIdType.WirelessDeviceId,
            )

    @markers.aws.unknown
    def test_wireless_gateways(self, aws_client):
        wireless_gateway_name = f"wd-{short_uid()}"

        gateway_before_count = len(
            aws_client.iotwireless.list_wireless_gateways()["WirelessGatewayList"]
        )
        result = aws_client.iotwireless.create_wireless_gateway(
            Name=wireless_gateway_name, LoRaWAN={}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert "Id" in result
        gateway_id = result["Id"]

        # list wireless_gateway
        result = aws_client.iotwireless.list_wireless_gateways()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["WirelessGatewayList"]) == gateway_before_count + 1

        # get wireless_gateway
        result = aws_client.iotwireless.get_wireless_gateway(
            Identifier=gateway_id,
            IdentifierType=WirelessGatewayIdType.WirelessGatewayId,
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["Name"] == wireless_gateway_name

        # delete wireless_gateway
        result = aws_client.iotwireless.delete_wireless_gateway(Id=gateway_id)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotwireless.exceptions.ResourceNotFoundException):
            aws_client.iotwireless.get_wireless_gateway(
                Identifier=gateway_id,
                IdentifierType=WirelessGatewayIdType.WirelessGatewayId,
            )

    @markers.aws.unknown
    def test_device_profiles(self, aws_client):
        device_profile_name = f"wd-{short_uid()}"

        profile_before_count = len(
            aws_client.iotwireless.list_device_profiles()["DeviceProfileList"]
        )
        result = aws_client.iotwireless.create_device_profile(Name=device_profile_name, LoRaWAN={})
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert "Id" in result
        profile_id = result["Id"]

        # list device_profile
        result = aws_client.iotwireless.list_device_profiles()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["DeviceProfileList"]) == profile_before_count + 1

        # get device_profile
        result = aws_client.iotwireless.get_device_profile(Id=profile_id)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["Name"] == device_profile_name

        # delete device_profile
        result = aws_client.iotwireless.delete_device_profile(Id=profile_id)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotwireless.exceptions.ResourceNotFoundException):
            aws_client.iotwireless.get_device_profile(Id=profile_id)
