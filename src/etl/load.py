import logging
from pathlib import Path
from typing import Dict, List
import json

from src.etl.extract import EndpointEnum, create_items, query_graphql
from src.etl.transform import extract_ids_from_query
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models import DeviceStatusOptions, WritableDevice
from src.services.netbox.queries import generate_device_creation_payload
from src.services.xen.client import XenAPIClient
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
        log.info(f"XEN API returned {len(xen_hosts_data)} Hosts")

        log.info("Creating WritableDevice object to push to NetBox")
        for host in xen_hosts_data:
            log.debug(json.dumps(host.model_dump(), indent=2))
            query, variables = generate_device_creation_payload(
                device_type=host.bios_strings.system_product_name,
                site="hfm",
                location="7",
                platform=host.version[:-2],
                cluster=host.name_label,
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
            devices_to_create.append(
                WritableDevice(
                    name=host.name_label,
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
