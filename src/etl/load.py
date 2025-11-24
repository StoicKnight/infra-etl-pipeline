import logging
from pathlib import Path
from typing import Dict, List, Any
import json

from src.etl.extract import EndpointEnum, create_items, query_graphql
from src.etl.transform import extract_core_os_pattern, extract_ids_from_query
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models import (
    DeviceStatusOptions,
    VMStatusOptions,
    WritableDevice,
    WritableVirtualDisk,
    WritableVirtualMachine,
)
from src.services.netbox.queries import (
    generate_device_query_payload,
    generate_vdisk_query_payload,
    generate_vm_query_payload,
)
from src.services.xen.client import XenAPIClient
from src.services.xen.models import VirtualMachine
from src.utils.csv import write_csv

log = logging.getLogger(__name__)


def generate_report_stdout(
    source_file_name: str,
    updatable: List[Dict[str, str]],
    higher_version: List[Dict[str, str]],
    unresponsive: List[str],
) -> None:
    header = f"--- Report for {source_file_name} ---"
    print(f"\n{header}")

    print(f"\nFound {len(updatable)} minions that need an update:")
    for minion in updatable:
        print(f"  - {minion}")

    print(f"\nFound {len(higher_version)} minions with a higher version:")
    for minion in higher_version:
        print(f"  - {minion}")

    print(f"\nFound {len(unresponsive)} unresponsive minions:")
    for minion_id in unresponsive:
        print(f"  - {minion_id}")
    print("-" * len(header))


def export_report_to_csv(
    source_file_name: str,
    updatable: List[Dict[str, str]],
    higher_version: List[Dict[str, str]],
    unresponsive: List[str],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_filename = Path(source_file_name).stem + "_report.csv"
    csv_filepath = output_dir / csv_filename

    header = ["minion_id", "installed_version", "status"]
    rows = []

    for minion in updatable:
        minion_id, version = list(minion.items())[0]
        rows.append([minion_id, version, "Needs Update"])

    for minion in higher_version:
        minion_id, version = list(minion.items())[0]
        rows.append([minion_id, version, "Higher Version"])

    for minion_id in unresponsive:
        rows.append([minion_id, "N/A", "Unresponsive"])

    try:
        write_csv(csv_filepath, header, rows)
    except Exception as e:
        log.error(f"Unhandled exceprion exporting report to csv: {e}")


async def load_hosts_netbox(netbox_client: NetBoxAPIClient, xen_client: XenAPIClient):
    devices_to_create = []
    query_ids_results = {}
    try:
        xen_hosts_data = await xen_client.hosts.get_all()
        log.info(f"Read {len(xen_hosts_data)} Hosts from Xen-Orchestra.")  # pyright: ignore

        for host in xen_hosts_data:
            log.debug(json.dumps(host.model_dump(), indent=2))  # pyright: ignore
            query, variables = generate_device_query_payload(
                device_type=host.bios_strings.system_product_name,  # pyright: ignore
                site="hfm",
                platform=extract_core_os_pattern(host.version),  # pyright: ignore
                cluster=host.name_label,  # pyright: ignore
                tenant="infra",
                role="hypervisor",
            )
            log.info("Get list of available device types.")
            query_ids_results = await query_graphql(
                client=netbox_client,
                query=query,
                variables=variables,
            )
            create_devices_ids = extract_ids_from_query(query_ids_results)
            log.info("Creating WritableDevice object to push to NetBox")
            devices_to_create.append(
                WritableDevice(
                    name=host.name_label,  # pyright: ignore
                    device_type=create_devices_ids.get("deviceType", 0),
                    site=create_devices_ids.get("site", 0),
                    location=create_devices_ids.get("location", 0),
                    platform=create_devices_ids.get("platform", 0),
                    cluster=create_devices_ids.get("cluster", 0),
                    tenant=create_devices_ids.get("tenant", 0),
                    role=create_devices_ids.get("role", 0),
                    status=DeviceStatusOptions.ACTIVE,
                    description="",
                )
            )
        log.info("Starting device creation...")
        created_devices = await create_items(
            netbox_client, EndpointEnum.DEVICE, data=devices_to_create
        )
        log.info(f"SUCCESS: Created {len(created_devices)} devices.")

    except Exception:
        log.exception(
            "An unexpected error occurred, when loading HOSTS data to NetBox."
        )


async def load_vms_netbox(netbox_client: NetBoxAPIClient, xen_client: XenAPIClient):
    vms_to_create = []
    query_ids_results = {}
    try:
        xen_vms_data: List[VirtualMachine] = await xen_client.vms.get_all()  # pyright: ignore
        log.info(f"Read {len(xen_vms_data)} VMs from Xen-Orchestra.")

        for vm in xen_vms_data:
            if vm.affinityHost is not None:
                asset = vm.affinityHost
            else:
                asset = vm.container
            log.info(f"Processing VM '{vm.name_label}': {vm.id}")
            query, variables = generate_vm_query_payload(
                device="",
                asset_tag=str(asset),
                platform=extract_core_os_pattern(str(vm.os_version.name)),  # pyright: ignore
                cluster="",
            )
            log.info("Query IDs for the VM to be created.")
            query_ids_results = await query_graphql(
                client=netbox_client,
                query=query,
                variables=variables,
            )
            create_vms_ids = extract_ids_from_query(query_ids_results)
            log.info("Creating 'WritableVirtualMachine' object to push to NetBox")
            vms_to_create.append(
                WritableVirtualMachine(
                    name=vm.name_label,
                    device=create_vms_ids.get("device", 0),
                    cluster=create_vms_ids.get("cluster", 0),
                    site=create_vms_ids.get("site", 0),
                    platform=create_vms_ids.get("platform", 23),  # 23: N/A Option
                    status=VMStatusOptions.ACTIVE,
                    memory=vm.memory.size // 1024 // 1024,  # pyright: ignore
                    vcpus=vm.CPUs.max,  # pyright: ignore
                    serial=vm.id,
                )
            )
        log.info("Starting device creation...")
        created_devices = await create_items(
            netbox_client, EndpointEnum.VIRTUAL_MACHINE, data=vms_to_create
        )
        log.info(f"SUCCESS: Created {len(created_devices)} devices.")

    except Exception:
        log.exception("An unexpected error occurred, when loading VMS data to NetBox.")


# FIX: The ids need to be integers
async def attach_vdisk_vm(netbox_client: NetBoxAPIClient, xen_client: XenAPIClient):
    try:
        xen_vms: List[VirtualMachine] = await xen_client.vms.get_all()  # pyright: ignore
        log.info(f"Read {len(xen_vms)} VMs from Xen_Orchestra.")
        for vm in xen_vms:
            await _process_single_vm(netbox_client, xen_client, vm)
    except Exception:
        log.exception(
            "An unexpected error occurred while attaching virtual disks to VMs."
        )


async def _process_single_vm(
    netbox_client: NetBoxAPIClient, xen_client: XenAPIClient, vm: VirtualMachine
):
    xen_disks = await xen_client.vms.get_vdisk(vm.id)
    if not xen_disks:
        return
    query, variables = generate_vdisk_query_payload(
        virtual_machine=vm.name_label, uuid=vm.id
    )
    nb_result = await query_graphql(
        client=netbox_client,
        query=query,
        variables=variables,
    )
    nb_data = extract_ids_from_query(nb_result)
    nb_vm_ids = nb_data.get("virtual_machine", [])
    if not nb_vm_ids:
        log.warning(
            f"VM '{vm.name_label}' not found in NetBox (by Query). Skipping disk sync."
        )
        return
    nb_vm_id = nb_vm_ids[0]
    existing_disks_map = _parse_existing_netbox_disks(nb_data.get("virtual_disks", []))
    disks_to_create = []
    for vdisk in xen_disks:
        size_mb = vdisk.size // 1024 // 1024  # pyright: ignore
        if vdisk.name_label in existing_disks_map:  # pyright: ignore
            existing_size = existing_disks_map[vdisk.name_label]  # pyright: ignore
            if existing_size == size_mb:
                log.info(
                    f"Skipping '{vdisk.name_label}': Exists with matching size ({size_mb} MB)."  # pyright: ignore
                )
                continue
            else:
                log.warning(
                    f"Disk '{vdisk.name_label}' exists but size mismatch (NetBox: {existing_size} MB, Xen: {size_mb} MB). Skipping creation to avoid duplicates."  # pyright: ignore
                )
                continue
        log.info(
            f"Queueing creation of vDisk '{vdisk.name_label}' ({size_mb} MB) for VM {vm.name_label}"
        )
        disks_to_create.append(
            WritableVirtualDisk(
                name=vdisk.name_label,  # pyright: ignore
                virtual_machine=int(nb_vm_id),
                size=size_mb,
            )
        )
    if disks_to_create:
        created_items = await create_items(
            netbox_client, EndpointEnum.VIRTUAL_DISK, data=disks_to_create
        )
        log.info(
            f"SUCCESS: Attached {len(created_items)} new virtual disk(s) to VM: {vm.name_label}."
        )


def _parse_existing_netbox_disks(nb_disks_data: Any) -> Dict[str, int]:
    disk_map = {}
    if isinstance(nb_disks_data, dict):
        nb_disks_data = [nb_disks_data]
    if not nb_disks_data:
        return {}
    for d in nb_disks_data:
        name = d.get("name")
        size = d.get("size")
        if name is not None:
            disk_map[name] = size
    return disk_map


# async def attach_vdisk_vm(netbox_client: NetBoxAPIClient, xen_client: XenAPIClient):
#     vdisks_to_create = []
#     query_ids_results = {}
#     try:
#         xen_vms_data: List[VirtualMachine] = await xen_client.vms.get_all()
#         log.info(f"Read {len(xen_vms_data)} VMs from Xen_Orchestra.")
#         for vm in xen_vms_data:
#             vdisks = await xen_client.vms.get_vdisk(vm.id)
#             for vdisk in vdisks:
#                 log.info(
#                     f"Processing vDisk '{vdisk.name_label}' from VM: {vm.name_label} - ID: {vdisk.id}"
#                 )
#                 query, variables = generate_vdisk_query_payload(
#                     virtual_machine=vm.name_label, uuid=vm.id
#                 )
#                 log.info("Query IDs for the vDisk to be created.")
#                 query_ids_results = await query_graphql(
#                     client=netbox_client,
#                     query=query,
#                     variables=variables,
#                 )
#                 create_vdisks_ids = extract_ids_from_query(query_ids_results)
#                 if (
#                     create_vdisks_ids["virtual_disks"]
#                     and create_vdisks_ids["virtual_disks"]["name"] == vdisk.name_label
#                 ):
#                     log.info(f"Virtual Disk {vdisk.name_label} skipped.")
#                     continue
#                 log.debug(f"Query Results: {create_vdisks_ids}")
#                 log.info("Creating 'WritableVirtualDisk' objects to push to NetBox")
#                 for id in create_vdisks_ids.get("virtual_machine", 0):
#                     vdisks_to_create.append(
#                         WritableVirtualDisk(
#                             name=vdisk.name_label,
#                             virtual_machine=id,
#                             size=vdisk.size // 1024 // 1024,
#                         )
#                     )
#                 created_virtual_disks = await create_items(
#                     netbox_client, EndpointEnum.VIRTUAL_DISK, data=vdisks_to_create
#                 )
#                 log.info(
#                     f"SUCCESS: Attached {len(created_virtual_disks)} virtual disk(s) to VM: {vm.name_label}."
#                 )
#     except Exception:
#         log.exception(
#             "An unexpected error occurred, when attaching vitrual disks to VMs."
#         )
