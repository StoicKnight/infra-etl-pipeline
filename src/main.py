import asyncio
import logging
import sys

from src.config import settings
from src.etl.extract import extract_data_from_files
from src.etl.load import export_report_to_csv, generate_report_stdout
from src.etl.transform import transform_minion_data
from src.logging import setup_logging
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.exceptions import NetBoxAPIError
from src.services.service_gateway import ServiceGateway

log = logging.getLogger(__name__)


async def test_netbox():
    """
    Example to test functionality of NetBoxAPIClient.
    """
    setup_logging()
    NETBOX_BASE_URL = str(settings.netbox.base_url)
    NETBOX_API_TOKEN = settings.netbox.api_token
    VERIFY_SSL = False
    DEVICE_ID = 1547
    VM_ID = 836
    IP_ADDRESS_ID = 13050

    log.info("Initializing NetBox API client...")
    client = NetBoxAPIClient(
        base_url=NETBOX_BASE_URL, token=NETBOX_API_TOKEN, verify_ssl=VERIFY_SSL
    )
    device_count = 0
    vm_count = 0
    ip_count = 0

    try:
        log.info("Fetching devices from NetBox...")
        async for device in client.devices.list():
            device_count += 1
            print(200 * "=")
            log.info(f"Device #{device_count}: {device.name}")
            print(
                f"IPs: [{device.primary_ip.address if device.primary_ip else ""},{device.oob_ip.address if device.oob_ip else ""}]"
            )
            print(200 * "=")
        log.info(f"\nFinished processing. Total devices found: {device_count}")

        log.info(f"Fetching device ID: {DEVICE_ID}")
        single_device = await client.devices.get(DEVICE_ID)
        log.info(f"Successfully fetched device: {single_device.name}")

        log.info("Fetching VMs from NetBox...")
        async for vm in client.vms.list():
            vm_count += 1
            print(200 * "=")
            log.info(f"VM #{vm_count}: {vm.name}")
            print(f"IPs: [{vm.primary_ip.address if vm.primary_ip else ""}]")
            print(200 * "=")
        log.info(f"\nFinished processing. Total VMs found: {vm_count}")

        log.info(f"Fetching VM ID: {VM_ID}")
        single_vm = await client.vms.get(VM_ID)
        log.info(f"Successfully fetched VM: {single_vm.name}")

        log.info("Fetching IP addresses from NetBox...")
        async for ip in client.ips.list():
            ip_count += 1
            print(200 * "=")
            log.info(f"IP #{vm_count}: {ip.display}")
            print(f"Address: [{ip.address}]")
            print(200 * "=")
        log.info(f"\nFinished processing. Total IPs found: {ip_count}")

        log.info(f"Fetching IP address ID: {IP_ADDRESS_ID}")
        single_ip = await client.ips.get(IP_ADDRESS_ID)
        log.info(f"Successfully fetched IP: {single_ip.address}")
    except NetBoxAPIError as e:
        log.error(f"API error: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
    finally:
        log.info("Closing API client.")
        await client.close()


async def main():
    setup_logging()
    log.info("Application starting.")

    json_files = list(settings.paths.data_dir.glob("*.json"))
    if not json_files:
        print(
            f"Error: No JSON files found in directory: {settings.paths.data_dir}",
            file=sys.stderr,
        )
        return

    print(f"Found {len(json_files)} files to process in '{settings.paths.data_dir}'...")

    all_minion_data = extract_data_from_files(json_files)
    if not any(all_minion_data):
        print(
            "Error: No minion data could be successfully processed from any file.",
            file=sys.stderr,
        )
        return

    processed_data = transform_minion_data(
        settings.salt.target_version,
        all_minion_data,
    )

    for file_path, (updatable, higher, unresponsive) in zip(json_files, processed_data):
        report_title = file_path.name
        generate_report_stdout(report_title, updatable, higher, unresponsive)

        export_report_to_csv(
            report_title, updatable, higher, unresponsive, settings.paths.reports_dir
        )

    try:
        gateway = ServiceGateway(settings)

        log.info("Requesting service data bundle from gateway.")
        service_data = await gateway.get_all_service_data(salt_target="")
        minion_count = len(service_data.salt.return_data[0].root)
        log.info(f"Gateway returned data for {minion_count} minions.")

        for minion_id, grains in service_data.salt.return_data[0].root.items():
            print(f"OS for {minion_id}: {grains.osfinger}")

    except Exception:
        log.exception("An unhandled exception occurred in the main application.")

    await test_netbox()
    log.info("Application finished.")


if __name__ == "__main__":
    asyncio.run(main())
