import asyncio
import logging

import httpx

from src.config import settings
from src.logging import setup_logging
from src.services.netbox.endpoints.dcim import DevicesEndpoints
from src.services.netbox.endpoints.ipam import IPAddressesEndpoints
from src.services.netbox.endpoints.virtualization import VMEndpoints
from src.services.netbox.exceptions import NetBoxAPIError

log = logging.getLogger(__name__)


class NetBoxAPIClient:
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=20.0,
            verify=verify_ssl,
        )
        self.devices = DevicesEndpoints(self._client)
        self.vms = VMEndpoints(self._client)
        self.ips = IPAddressesEndpoints(self._client)

    async def close(self):
        await self._client.aclose()


async def main():
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


if __name__ == "__main__":
    asyncio.run(main())
