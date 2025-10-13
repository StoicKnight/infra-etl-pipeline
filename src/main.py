import asyncio
import logging
import sys
from typing import Any, List

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

    # try:
    #     log.info("Initializing NetBox API client...")
    #     devices_list: List[Any] = []
    #     netbox_client = NetBoxAPIClient(
    #         base_url=NETBOX_BASE_URL, token=NETBOX_API_TOKEN, verify_ssl=VERIFY_SSL
    #     )
    #     devices_list = await list_netbox_devices(netbox_client)
    #     device_parser = create_parser(DEVICE_COLUMN_MAP)
    #     headers, rows = device_parser(devices_list)
    #     write_csv("output_devices.csv", headers, rows)
    #
    #     vms_list = await list_netbox_vms(netbox_client)
    #     vm_parser = create_parser(VM_COLUMN_MAP)
    #     headers, rows = vm_parser(vms_list)
    #     write_csv("output_vms.csv", headers, rows)
    # except Exception as e:
    #     log.error(f"Unhandled error: {e}")
    # finally:
    #     log.info("Closing NetBox API client")
    #     await netbox_client.close()

    SALT_TARGET = "*"
    SALT_TARGET_TYPE = "glob"
    try:
        log.info("Initializing Salt API client.")
        salt_client = SaltAPIClient(
            api_url=settings.salt.api_url,
            username=settings.salt.username,
            password=settings.salt.password,
        )
        grains_data = await salt_client.get_minion_grains(SALT_TARGET, SALT_TARGET_TYPE)
        minion_count = len(grains_data)
        log.info(f"Gateway returned data for {minion_count} minions.")

        for minion_id, grains in grains_data.salt.return_data[0].root.items():
            print(f"OS for {minion_id}: {grains.osfinger}")

    except Exception as e:
        log.exception(f"Unhandled error from Salt API: {e}")
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
