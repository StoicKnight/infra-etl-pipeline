import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.services.netbox.client import NetBoxAPIClient

log = logging.getLogger(__name__)


def load_json_data(file_path: Path) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return {}


def extract_json_data(file_paths: List[Path]) -> List[Dict[str, Any]]:
    return list(map(load_json_data, file_paths))


async def list_netbox_ips(
    client: NetBoxAPIClient,
):
    ips_list = []
    try:
        log.info("Fetching IP addresses from NetBox...")
        async for ip in client.ips.list():
            ips_list.append(ip)
        log.info(f"Fetched {len(ips_list)} IPs.")
        return ips_list
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")


async def list_netbox_vms(
    client: NetBoxAPIClient,
):
    vms_list = []
    try:
        log.info("Fetching Virtual Machines from NetBox...")
        async for ip in client.vms.list():
            vms_list.append(ip)
        log.info(f"Fetched {len(vms_list)} VMs.")
        return vms_list
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")


async def list_netbox_devices(
    client: NetBoxAPIClient,
):
    devices_list = []
    try:
        log.info("Fetching Devices from NetBox...")
        async for ip in client.devices.list():
            devices_list.append(ip)
        log.info(f"Fetched {len(devices_list)} Devices.")
        return devices_list
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
