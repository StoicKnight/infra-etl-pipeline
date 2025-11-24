import pytest
import logging
from unittest.mock import MagicMock, AsyncMock

from services.xen.models import VirtualDisk, VirtualMachine

from src.etl.load import attach_vdisk_vm
from src.etl.extract import EndpointEnum


class WritableVirtualDisk:
    def __init__(self, name, virtual_machine, size):
        self.name = name
        self.virtual_machine = virtual_machine
        self.size = size

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.virtual_machine == other.virtual_machine
            and self.size == other.size
        )

    def __repr__(self):
        return f"WritableVirtualDisk(name={self.name}, vm={self.virtual_machine}, size={self.size})"


@pytest.fixture
def mock_netbox_client():
    return MagicMock(name="NetBoxAPIClient")


@pytest.fixture
def mock_xen_client():
    client = MagicMock(name="XenAPIClient")
    client.vms.get_all = AsyncMock()
    client.vms.get_vdisk = AsyncMock()
    return client


@pytest.fixture
def mock_external_funcs(mocker):
    module_path = "src.etl.load"
    mock_gen_query = mocker.patch(f"{module_path}.generate_vdisk_query_payload")
    mock_gen_query.return_value = ("default_query", {})
    return {
        "generate_query": mock_gen_query,
        "query_graphql": mocker.patch(
            f"{module_path}.query_graphql", new_callable=AsyncMock
        ),
        "extract_ids": mocker.patch(f"{module_path}.extract_ids_from_query"),
        "create_items": mocker.patch(
            f"{module_path}.create_items", new_callable=AsyncMock
        ),
        "WritableVirtualDisk": mocker.patch(
            f"{module_path}.WritableVirtualDisk", side_effect=WritableVirtualDisk
        ),
        "EndpointEnum": mocker.patch(f"{module_path}.EndpointEnum", EndpointEnum),
    }


@pytest.mark.asyncio
async def test_attach_vdisk_happy_path_new_disk(
    mock_netbox_client, mock_xen_client, mock_external_funcs
):
    vm = VirtualMachine(id="vm-123", name_label="MyServer")
    vdisk = VirtualDisk(
        id="vd-1", name_label="System Disk", size_bytes=10485760 * 1024
    )  # 10GB in bytes
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [vdisk]
    mock_external_funcs["generate_query"].return_value = ("query...", {})
    mock_external_funcs["query_graphql"].return_value = {"some": "json"}
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [999],  # NetBox ID
        "virtual_disks": [],  # No existing disks
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    expected_disk = WritableVirtualDisk(
        name="System Disk",
        virtual_machine=999,
        size=10240,  # 10 GB in MB
    )
    mock_external_funcs["create_items"].assert_called_once()
    call_args = mock_external_funcs["create_items"].call_args
    assert call_args[1]["data"] == [expected_disk]
    assert call_args[0][1] == EndpointEnum.VIRTUAL_DISK


@pytest.mark.asyncio
async def test_attach_vdisk_skip_existing_exact_match(
    mock_netbox_client, mock_xen_client, mock_external_funcs, caplog
):
    caplog.set_level(logging.INFO)
    vm = VirtualMachine(id="vm-123", name_label="MyServer")
    vdisk = MockVDisk(
        id="vd-1", name_label="Data", size_bytes=50 * 1024 * 1024
    )  # 50 MB
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [vdisk]
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [999],
        "virtual_disks": [{"name": "Data", "size": 50}],
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["create_items"].assert_not_called()
    assert "Skipping 'Data': Exists with matching size" in caplog.text


@pytest.mark.asyncio
async def test_attach_vdisk_skip_size_mismatch(
    mock_netbox_client, mock_xen_client, mock_external_funcs, caplog
):
    vm = VirtualMachine(id="vm-123", name_label="MyServer")
    vdisk = MockVDisk(
        id="vd-1", name_label="Data", size_bytes=100 * 1024 * 1024
    )  # 100 MB
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [vdisk]
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [999],
        "virtual_disks": [{"name": "Data", "size": 50}],
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["create_items"].assert_not_called()
    assert "size mismatch" in caplog.text


@pytest.mark.asyncio
async def test_vm_not_found_in_netbox(
    mock_netbox_client, mock_xen_client, mock_external_funcs, caplog
):
    vm = VirtualMachine(id="vm-123", name_label="GhostServer")
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [MockVDisk("1", "D", 100)]
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [],
        "virtual_disks": [],
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["create_items"].assert_not_called()
    assert "VM 'GhostServer' not found in NetBox" in caplog.text


@pytest.mark.asyncio
async def test_mixed_creation_one_new_one_existing(
    mock_netbox_client, mock_xen_client, mock_external_funcs
):
    vm = VirtualMachine(id="vm-1", name_label="DB")
    disk_a_new = MockVDisk("d1", "Disk A", 10 * 1024 * 1024)  # 10 MB
    disk_b_old = MockVDisk("d2", "Disk B", 20 * 1024 * 1024)  # 20 MB
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [disk_a_new, disk_b_old]
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [55],
        "virtual_disks": [{"name": "Disk B", "size": 20}],
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["create_items"].assert_called_once()
    created_data = mock_external_funcs["create_items"].call_args[1]["data"]
    assert len(created_data) == 1
    assert created_data[0].name == "Disk A"
    assert created_data[0].size == 10


@pytest.mark.asyncio
async def test_global_exception_handling(mock_netbox_client, mock_xen_client, caplog):
    mock_xen_client.vms.get_all.side_effect = Exception("Network Down")
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    assert "An unexpected error occurred" in caplog.text


@pytest.mark.asyncio
async def test_empty_xen_disks(
    mock_netbox_client, mock_xen_client, mock_external_funcs
):
    vm = VirtualMachine(1, "EmptyVM")
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = []  # No disks
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["query_graphql"].assert_not_called()
    mock_external_funcs["create_items"].assert_not_called()


@pytest.mark.asyncio
async def test_netbox_disk_single_dict_edge_case(
    mock_netbox_client, mock_xen_client, mock_external_funcs
):
    vm = VirtualMachine(id="1", name_label="VM")
    vdisk = MockVDisk("d1", "Disk A", 10 * 1024 * 1024)
    mock_xen_client.vms.get_all.return_value = [vm]
    mock_xen_client.vms.get_vdisk.return_value = [vdisk]
    mock_external_funcs["extract_ids"].return_value = {
        "virtual_machine": [1],
        "virtual_disks": {"name": "Disk A", "size": 10},
    }
    await attach_vdisk_vm(mock_netbox_client, mock_xen_client)
    mock_external_funcs["create_items"].assert_not_called()
