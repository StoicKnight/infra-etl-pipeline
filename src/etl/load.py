import logging
from pathlib import Path
import json

from src.etl.extract import EndpointEnum, create_items, query_graphql
from src.etl.transform import extract_core_os_pattern, flatten_to_target
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models import (
    DeviceStatusOptions,
    IPStatusOptions,
    VMStatusOptions,
    WritableDevice,
    WritableIPAddress,
    WritableVirtualDisk,
    WritableVirtualMachine,
)
from src.services.netbox.queries import (
    generate_device_query_payload,
    generate_vm_query_payload,
)
from src.services.xen.client import XenAPIClient
from src.services.xen.models import (
    VirtualDisk,
    VirtualMachine,
    VirtualMachineDevice,
    Host,
)
from src.utils.csv import write_csv

log = logging.getLogger(__name__)


def generate_report_stdout(
    source_file_name,
    updatable,
    higher_version,
    unresponsive,
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
    source_file_name,
    updatable,
    higher_version,
    unresponsive,
    output_dir,
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
    try:
        xen_hosts_data: list[Host] = await xen_client.hosts.get_all()
        log.info(f"Read {len(xen_hosts_data)} Hosts from Xen-Orchestra.")

        for host in xen_hosts_data:
            log.debug(json.dumps(host.model_dump(), indent=2))
            query, variables = generate_device_query_payload(
                device_model=host.bios_strings.system_product_name,
                site="hfm",
                platform=extract_core_os_pattern(host.version),
                cluster_name=host.name_label,
                tenant="infra",
                role="hypervisor",
            )
            log.info("Get list of available device types.")
            query_response = await query_graphql(
                client=netbox_client,
                query=query,
                variables=variables,
            )
            query_device = flatten_to_target(query_response)
            device_ids = query_device.get("device", None)[0]
            log.info("Creating WritableDevice object to push to NetBox")
            devices_to_create.append(
                WritableDevice(
                    name=host.name_label,
                    device_type=device_ids["device_type"].get("id", 27),
                    site=device_ids.get("site", 0),
                    # location=device_ids.get("location", 0),
                    platform=device_ids.get("platform", 0),
                    cluster=device_ids.get("cluster", 0),
                    tenant=device_ids.get("tenant", 0),
                    role=device_ids.get("role", 0),
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
    try:
        xen_vms_data: list[VirtualMachine] = await xen_client.vms.get_all()
        log.info(f"Read {len(xen_vms_data)} VMs from Xen-Orchestra.")

        for vm in xen_vms_data:
            if vm.affinityHost is not None:
                serial = vm.affinityHost
            else:
                serial = vm.container
            log.info(f"Processing VM '{vm.name_label}': {vm.id}")
            query, variables = generate_device_query_payload(
                device_name="",
                uuid=str(serial),
                platform=extract_core_os_pattern(str(vm.os_version.name)),
                cluster_name="",
            )
            log.info("Query IDs for the VM to be created.")
            query_response = await query_graphql(
                client=netbox_client,
                query=query,
                variables=variables,
            )
            query_vm = flatten_to_target(query_response)
            vm_ids = query_vm.get("virtual_machine", None)[0]
            log.info("Creating 'WritableVirtualMachine' object to push to NetBox")
            vms_to_create.append(
                WritableVirtualMachine(
                    name=vm.name_label,
                    device=vm_ids.get("device", 0),
                    cluster=vm_ids["cluster"].get("id", 0),
                    site=vm_ids.get("site", 0),
                    platform=vm_ids.get("platform", 23),
                    status=VMStatusOptions.ACTIVE,
                    memory=vm.memory.size // 1024 // 1024,
                    vcpus=vm.CPUs.max,
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


async def attach_vdisk_to_vm(netbox_client: NetBoxAPIClient, xen_client: XenAPIClient):
    try:
        xen_vms: list[VirtualMachine] = await xen_client.vms.get_all()
        log.info(f"Read {len(xen_vms)} VMs from Xen_Orchestra.")
        for vm in xen_vms:
            await _process_single_vm(netbox_client, xen_client, vm)
    except Exception:
        log.exception(
            "An unexpected error occurred while attaching virtual disks to VMs."
        )


async def _process_single_vm(
    netbox_client: NetBoxAPIClient,
    xen_client: XenAPIClient,
    existing_vm: VirtualMachine,
):
    new_vdisks = await _parse_vm_vdisks(xen_client=xen_client, vm_id=existing_vm.id)
    query, variables = generate_vm_query_payload(
        vm_name=existing_vm.name_label, uuid=existing_vm.id
    )
    nb_query_result = await query_graphql(
        client=netbox_client,
        query=query,
        variables=variables,
    )
    nb_vms = nb_query_result["data"]["virtual_machine"]
    if not isinstance(nb_vms, list) or len(nb_vms) != 1:
        log.warning(
            f"The query results for '{existing_vm.name_label}' returned invalid data: {nb_vms}"
        )
        return
    existing_vdisks = nb_vms[0]["virtualdisks"]
    vdisks_to_create = []
    for new_vdisk in new_vdisks:
        if not _process_existing_netbox_vdisks(
            existing_vdisks, new_vdisk["name"], new_vdisk["id"], new_vdisk["size"]
        ):
            continue
        if new_vdisk["is_cd_drive"]:
            continue
        log.info(
            f"Queueing creation of vDisk '{new_vdisk['name']}' ({new_vdisk['size']} MB) for VM: {existing_vm.name_label}"
        )
        vdisks_to_create.append(
            WritableVirtualDisk(
                name=new_vdisk["name"][:64],
                virtual_machine=int(nb_vms[0]["id"]),
                description=new_vdisk["id"],
                size=new_vdisk["size"],
            )
        )
    if vdisks_to_create:
        created_items = await create_items(
            netbox_client, EndpointEnum.VIRTUAL_DISK, data=vdisks_to_create
        )
        log.info(
            f"SUCCESS: Attached {len(created_items)} new virtual disk(s) to VM: {existing_vm.name_label}."
        )


def _process_existing_netbox_vdisks(
    existing_vdisks, new_vdisk_name, new_vdisk_id, new_vdisk_size
):
    if existing_vdisks:
        for existing_vdisk in existing_vdisks:
            log.debug(
                f"Checking if vDisk '{existing_vdisk['description']}' already exists"
            )
            log.debug(
                f"Comparing vDisk size: New: ['{new_vdisk_name}': '{new_vdisk_id}'] and Existing: ['{existing_vdisk['name']}': '{existing_vdisk['description']}'] => {new_vdisk_size} =? {existing_vdisk['size']}'"
            )
            if (
                new_vdisk_name == existing_vdisk["name"]
                and new_vdisk_id == existing_vdisk["description"]
            ):
                if existing_vdisk["size"] == new_vdisk_size:
                    log.info(
                        f"Skipping '{new_vdisk_name}': Exists with matching size ({existing_vdisk['size']} MB)."
                    )
                    return False
                else:
                    log.warning(
                        f"Disk '{new_vdisk_name}' exists but size mismatch (NetBox: {existing_vdisk['size']} MB, Xen: {new_vdisk_size} MB). Skipping creation to avoid duplicates."
                    )
                    # NOTE: this will change to update the vDisk values
                    return False
    return True


async def _parse_vm_vdisks(xen_client: XenAPIClient, vm_id):
    list_vdisks = []
    xen_vdisks: list[VirtualDisk] = await xen_client.vms.get_vdisk(vm_id)
    xen_vm_devices: list[VirtualMachineDevice] = await xen_client.vbds.get_all(
        vm_id=vm_id
    )
    if not xen_vdisks:
        return []
    for vdisk in xen_vdisks:
        vdisk_data = {}
        for device in xen_vm_devices:
            if not device.vdi:
                continue
            if device.vdi == vdisk.id:
                vdisk_data["name"] = f"{vdisk.name_label} [{device.device}]"
                vdisk_data["size"] = vdisk.size // 1024 // 1024
                vdisk_data["id"] = vdisk.id
                vdisk_data["device"] = device.device
                vdisk_data["is_cd_drive"] = device.is_cd_drive
        list_vdisks.append(vdisk_data)
    return list_vdisks


async def attach_ip_address_to_vm(
    netbox_client: NetBoxAPIClient, xen_client: XenAPIClient
):
    try:
        xen_vms: list[VirtualMachine] = await xen_client.vms.get_all()
        log.info(f"Read {len(xen_vms)} VMs from Xen_Orchestra.")
        for vm in xen_vms:
            ips_to_create = []
            if vm.addresses:
                query, variables = generate_vm_query_payload(
                    vm_name=vm.name_label, uuid=vm.id
                )
                query_response = await query_graphql(
                    client=netbox_client,
                    query=query,
                    variables=variables,
                )
                query_vm = flatten_to_target(query_response)
                print("*" * 30)
                print(f"Query Response: {query_response}")
                print("*" * 30)
                if not query_vm:
                    continue
                vm_ids = query_vm.get("virtual_machine", None)[0]
                print("*" * 30)
                print(f"Existing VM: {vm_ids} =? New VM: {vm.addresses}")
                print("*" * 30)
                for ip_type, ip_address in vm.addresses.items():
                    if "ipv4" in ip_type:
                        print(f"Create new IP Address on NetBox: {ip_address}")
                        ip_address = query_response["data"]["virtual_machine"][0][
                            "interfaces"
                        ][0]["ip_addresses"][0]["address"]
                        if not (ip_address) or not (ip):
                            continue
                        ips_to_create.append(
                            WritableIPAddress(
                                address=f"{ip_address}/24",
                                status=IPStatusOptions.ACTIVE,
                                assigned_object_type="virtualization.vminterface",
                                assigned_object_id=vm_ids["interfaces"][0].get("id", 0)
                                if isinstance(vm_ids["interfaces"][0], dict)
                                else vm_ids["interfaces"][0],
                            )
                        )
                if ips_to_create:
                    created_items = await create_items(
                        netbox_client, EndpointEnum.IP_ADDRESS, data=ips_to_create
                    )
                    log.info(
                        f"SUCCESS: Attached {len(created_items)} new IP(s) to VM: {vm.name_label}."
                    )
    except Exception:
        log.exception("An unexpected error occurred while attaching IPs to VMs.")
