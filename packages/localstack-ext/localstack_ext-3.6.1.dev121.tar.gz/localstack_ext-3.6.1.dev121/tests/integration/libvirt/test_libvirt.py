import os

import pytest
from localstack.pro.core.utils.libvirt.configuration import (
    domain_xml,
    storage_pool_xml,
    storage_volume_xml,
)
from localstack.pro.core.utils.libvirt.core import LibvirtClient, LibvirtError
from localstack.pro.core.utils.libvirt.models import Domain, DomainState, Volume
from localstack.utils.files import new_tmp_dir
from localstack.utils.strings import long_uid, short_uid


class TestLibvirtClient:
    """
    Tests the wrapper library using the test hypervisor driver: https://libvirt.org/drvtest.html
    Cleanups are not necessary because everything is in-memory.
    """

    @pytest.fixture
    def client(self):
        """This fixture returns an instance of the wrapper client to be tested."""
        return LibvirtClient(uri="test:///default")

    def test_domain_crud(self, client):
        # Create a domain
        domain_name = f"domain-{short_uid()}"
        domain_uuid = long_uid()
        domain_memory = 4042
        domain_vcpu = 42

        xml = domain_xml(
            name=domain_name,
            uuid=domain_uuid,
            memory=domain_memory,
            vcpu=domain_vcpu,
            storage_volume_path="/dev/zero",
        )

        client.create_domain(xml)

        expected_domain = Domain(
            uuid=domain_uuid,
            name=domain_name,
            os_type="linux",
            state=DomainState.shutoff,
            memory=domain_memory,
            vcpu=domain_vcpu,
        )

        # Assert list_domains()
        assert expected_domain not in client.list_domains(inactive=False)
        assert expected_domain in client.list_domains(inactive=True)

        # Assert get_domain() on a non-running domain
        assert client.get_domain(name=domain_name) == expected_domain

        # Assert start_domain()
        client.start_domain(name=domain_name)
        expected_domain["state"] = DomainState.running
        assert expected_domain in client.list_domains(inactive=False)
        assert expected_domain in client.list_domains(inactive=True)

        # Assert stop_domain()
        client.stop_domain(name=domain_name)
        expected_domain["state"] = DomainState.shutoff
        assert expected_domain not in client.list_domains(inactive=False)
        assert expected_domain in client.list_domains(inactive=True)

        # Assert delete_domain()
        client.delete_domain(name=domain_name)
        assert expected_domain not in client.list_domains(inactive=False)
        assert expected_domain not in client.list_domains(inactive=True)
        with pytest.raises(LibvirtError) as exc:
            client.get_domain(name=domain_name)
        exc.match("Domain not found")

    def test_storage_pool_and_volume_crud(self, client):
        pool_name = f"pool-{short_uid()}"
        pool_directory = new_tmp_dir()  # the test driver does not actually use this directory

        xml = storage_pool_xml(pool_name, pool_directory)
        client.create_storage_pool(xml)

        # Assert list_volumes() in an empty pool
        assert client.list_volumes(pool_name) == []

        # Create a volume
        volume_name = f"volume-{short_uid()}.qcow2"
        volume_cap = 1024  # MiB

        expected_volume = Volume(
            name=volume_name,
            capacity=volume_cap,
            path=os.path.join(pool_directory, volume_name),
        )
        xml = storage_volume_xml(volume_name, pool_directory, volume_cap)

        client.create_volume(pool_name, xml)

        # Assert storage pool after volume is created
        pool_dict = client.get_storage_pool(pool_name)
        assert pool_dict["name"] == pool_name
        assert pool_dict["volumes"] == 1

        # Assert list_volumes()
        assert expected_volume in client.list_volumes(pool_name)

        # Assert get_volume()
        assert client.get_volume(pool_name, volume_name) == expected_volume

        # Clone volume
        clone_volume_name = f"clone-{volume_name}"
        clone_xml = storage_volume_xml(clone_volume_name, pool_directory, volume_cap)
        expected_clone_volume = Volume(
            name=clone_volume_name,
            capacity=volume_cap,
            path=os.path.join(pool_directory, clone_volume_name),
        )
        client.clone_volume(pool_name, volume_name, clone_xml)
        assert client.get_volume(pool_name, clone_volume_name) == expected_clone_volume
        assert expected_clone_volume in client.list_volumes(pool_name)

        # Enlarge the volume
        # NOTE: virStorageVolResize() is not supported by the test driver
        # new_volume_cap = 1024 * 2
        # expected_volume['capacity'] = new_volume_cap
        # client.resize_volume(pool_name, volume_name, new_volume_cap)
        # assert client.get_volume(pool_name, volume_name) == expected_volume

        # Ensure cloned volume is counted by the storage pool
        pool_dict = client.get_storage_pool(pool_name)
        assert pool_dict["volumes"] == 2

        # Delete all volumes
        # NOTE: virStorageVolWipe() is not supported by test driver
        client.delete_volume(pool_name, volume_name, wipe=False)
        assert expected_volume not in client.list_volumes(pool_name)
        client.delete_volume(pool_name, clone_volume_name, wipe=False)

        # Ensure storage pool has no volumes
        pool_dict = client.get_storage_pool(pool_name)
        assert pool_dict["volumes"] == 0

        # Delete storage pool
        client.delete_storage_pool(pool_name)

        with pytest.raises(LibvirtError) as exc:
            client.get_storage_pool(pool_name)
        exc.match(f"Storage pool not found: no storage pool with matching name '{pool_name}'")


class TestXmlConfig:
    """
    Sanity tests to ensure the XML config builders generate a proper XML.
    """

    def test_domain_config_generation(self):
        name = short_uid()
        uuid = long_uid()
        memory = 3232
        vcpu = 11
        storage_volume = "/foo/bar"
        cdrom_volume = "/lorem/ipsum"
        hypervisor = "plan9"

        xml = domain_xml(name, uuid, memory, vcpu, storage_volume, cdrom_volume, hypervisor)
        assert f'<domain type="{hypervisor}">' in xml
        assert f"<name>{name}</name>" in xml
        assert f"<uuid>{uuid}</uuid>" in xml
        assert f'<memory unit="MiB">{memory}</memory>' in xml
        assert f'<vcpu placement="static">{vcpu}</vcpu>' in xml
        assert f'<source file="{storage_volume}" />' in xml
        assert '<disk type="file" device="cdrom">' in xml

    def test_storage_pool_config_generation(self):
        name = short_uid()
        path = f"/{short_uid()}/bar"

        xml = storage_pool_xml(name, path)
        assert '<pool type="dir">' in xml
        assert f"<name>{name}</name>" in xml
        assert f"<path>{path}</path>" in xml

    def test_storage_volume_config_generation(self):
        name = short_uid()
        pool_dir = f"/{short_uid()}/bar"
        capacity = 1337
        fmt = "bochs"

        xml = storage_volume_xml(name, pool_dir, capacity, fmt)
        assert f"<name>{name}</name>" in xml
        assert f'<path>{pool_dir + "/" + name}</path>' in xml
        assert f'<capacity unit="MiB">{capacity}</capacity>' in xml
        assert f'<format type="{fmt}" />' in xml
