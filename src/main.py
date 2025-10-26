import asyncio
import logging
import random
import sys
from os import stat
from typing import Any, List

import httpx

from src.config import settings
from src.etl.extract import (
    list_netbox_devices,
    list_netbox_ips,
    list_netbox_vms,
)
from src.etl.load import export_report_to_csv, generate_report_stdout
from src.etl.transform import transform_minion_data
from src.logging import setup_logging
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models import (
    DeviceStatusOptions,
    PatchedDevice,
    PatchedDeviceWithId,
    WritableDevice,
)
from src.services.salt import exceptions
from src.services.salt.client import SaltAPIClient
from src.utils.csv import write_csv
from src.utils.parse import create_parser

log = logging.getLogger(__name__)


async def main():
    setup_logging()
    log.debug("Main function called...")

    NETBOX_BASE_URL = str(settings.netbox.base_url)
    NETBOX_API_TOKEN = settings.netbox.api_token
    VERIFY_SSL = settings.netbox.ssl
    DEVICE_COLUMN_MAP = settings.device_export_map
    VM_COLUMN_MAP = settings.vm_export_map
    log.info("Constructing the device objects...")
    status_list = list(DeviceStatusOptions)
    devices_to_create = []
    devices_to_update = []
    for i in range(45, 55):
        random_status = random.choice(status_list)
        devices_to_create.append(
            WritableDevice(
                name=f"my-test-server-2{i}",
                site=1,
                device_type=1,
                role=1,
                status=random_status.value,
            )
        )
        devices_to_update.append(
            PatchedDeviceWithId(
                id=i - 20,
                name=f"my-test-server-0{i-20}-updated",
                site=1,
                device_type=1,
                role=1,
                status=random_status.value,
            )
        )

    log.info("Initializing NetBox API client...")

    async with NetBoxAPIClient(
        base_url=NETBOX_BASE_URL, token=NETBOX_API_TOKEN
    ) as client:
        try:
            log.info("--- Creating a SINGLE device ---")
            single_device_to_create = WritableDevice(
                name="single-server-111",
                site=1,
                device_type=1,
                role=1,
                status=DeviceStatusOptions.FAILED,
            )
            created_device = await client.devices.create(single_device_to_create)
            log.info(f"SUCCESS: Created single device with ID: {created_device.id}")

            log.info("--- Updating a SINGLE device ---")
            single_device_to_update = PatchedDeviceWithId(
                id=25,
                name="single-server-25-updated",
                site=1,
                device_type=1,
                role=1,
                status=DeviceStatusOptions.ACTIVE,
            )
            updated_device = await client.devices.update(single_device_to_update)
            log.info(f"SUCCESS: Created single device with ID: {updated_device.id}")

            log.info("\n--- Creating MULTIPLE devices ---")
            created_devices = await client.devices.create(devices_to_create)
            log.info(f"SUCCESS: Created {len(created_devices)} devices.")
            created_ids = [d.id for d in created_devices]
            log.info(f"New IDs: {created_ids}")

            log.info("\n--- Updating MULTIPLE devices ---")
            updated_devices = await client.devices.update(devices_to_update)
            log.info(f"SUCCESS: Updated {len(updated_devices)} devices.")

            log.info("\n--- Deleting MULTIPLE devices ---")
            all_ids_to_delete = list(range(5, 15))
            if await client.devices.delete(all_ids_to_delete):
                log.info(f"SUCCESS: Deleted devices with IDs: {all_ids_to_delete}")

        except Exception as e:
            log.error(f"API ERROR: {e}")


# SALT_TARGET = "cy11*"
# SALT_TARGET_TYPE = "glob"
# try:
#     log.info("Initializing Salt API client.")
#     async with await SaltAPIClient.create(
#         api_url=settings.salt.api_url,
#         username=settings.salt.username,
#         password=settings.salt.password,
#     ) as salt_client:
#         minions_data = await salt_client.get_minion_grains(
#             SALT_TARGET, SALT_TARGET_TYPE
#         )
#         minion_count = len(minions_data.root)
#         log.info(f"Salt returned data for {minion_count} minions.")
#
#         for minion_id, grains in minions_data.root.items():
#             os_finger = grains.osfinger
#             print(f"Full list grains for {minion_id}:\n{grains}")
#             print(f"OS for {minion_id}: {os_finger}")
#             print(f"Hostname for {minion_id}: {grains.host}")
#
# except exceptions.SaltAPIError as e:
#     log.error(f"A Salt API error occurred: {e}", exc_info=True)
# except httpx.RequestError as e:
#     log.error(f"A network error occurred: {e}", exc_info=True)
# except Exception:
#     log.exception("An unexpected error occurred.")

# finally:
#     log.info("Closing Salt API client")
#     await salt_client.close()

# json_files = list(settings.paths.data_dir.glob("*.json"))
# if not json_files:
#     print(
#         f"Error: No JSON files found in directory: {settings.paths.data_dir}",
#         file=sys.stderr,
#     )
#     return
#
# print(f"Found {len(json_files)} files to process in '{settings.paths.data_dir}'...")
#
# all_minion_data = extract_data_from_files(json_files)
# if not any(all_minion_data):
#     print(
#         "Error: No minion data could be successfully processed from any file.",
#         file=sys.stderr,
#     )
#     return
#
# processed_data = transform_minion_data(
#     settings.salt.target_version,
#     all_minion_data,
# )
#
# for file_path, (updatable, higher, unresponsive) in zip(json_files, processed_data):
#     report_title = file_path.name
#     generate_report_stdout(report_title, updatable, higher, unresponsive)
#
#     export_report_to_csv(
#         report_title, updatable, higher, unresponsive, settings.paths.reports_dir
#     )


if __name__ == "__main__":
    asyncio.run(main())
