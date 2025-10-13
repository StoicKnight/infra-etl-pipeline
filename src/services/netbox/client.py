import logging

import httpx

from src.services.netbox.endpoints.dcim import DevicesEndpoints
from src.services.netbox.endpoints.ipam import IPAddressesEndpoints
from src.services.netbox.endpoints.virtualization import VMEndpoints

log = logging.getLogger(__name__)


class NetBoxAPIClient:
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json",
        }
        self.__client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=20.0,
            verify=verify_ssl,
        )
        self.devices = DevicesEndpoints(self.__client)
        self.vms = VMEndpoints(self.__client)
        self.ips = IPAddressesEndpoints(self.__client)

    async def close(self):
        await self.__client.aclose()
