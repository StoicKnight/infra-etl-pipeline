import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models.ip_address import IPAddress, IPAddressList

log = logging.getLogger(__name__)


class IPAddressesEndpoints:
    def __init__(self, client: httpx.AsyncClient):
        self.__client = client

    async def list(self) -> AsyncGenerator[IPAddress, None]:
        next_url: Optional[str] = "/api/ipam/ip-addresses/"
        try:
            while next_url:
                log.debug(f"Next URL: {next_url}")
                response = await self.__client.get(next_url)
                response.raise_for_status()
                ip_address_list = IPAddressList.model_validate(response.json())

                for ip_address in ip_address_list.results:
                    yield ip_address
                if ip_address_list.next:
                    next_url = str(ip_address_list.next)
                else:
                    next_url = None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "IP address list not found",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
            elif e.response.status_code in [401, 403]:
                raise NetBoxAPIError(
                    "Authentication failed",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
            else:
                raise NetBoxAPIError(
                    "API request failed",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e

    async def get(self, ip_address_id) -> IPAddress:
        url: str = f"/api/ipam/ip-addresses/{ip_address_id}/"
        log.debug(f"IP Address URL: {url}")
        try:
            response = await self.__client.get(url)
            response.raise_for_status()
            return IPAddress.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "IP address not found",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
            elif e.response.status_code in [401, 403]:
                raise NetBoxAPIError(
                    "Authentication failed",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
            else:
                raise NetBoxAPIError(
                    "API request failed",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
