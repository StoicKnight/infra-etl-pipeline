import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models.ip_address import (
    IPAddress,
    IPAddressCreate,
    IPAddressList,
    IPAddressUpdate,
)

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

    async def create_ip_address(
        self, ip_address: IPAddressCreate
    ) -> Optional[IPAddress]:
        url: str = "/api/ipam/ip-addresses/"
        payload = ip_address.model_dump(exclude_unset=True)
        try:
            response = await self.__client.post(url, json=payload)
            response.raise_for_status()
            if response.status_code == 201:
                log.info("IP Address created successfully (Status: 201 Created).")
                return IPAddress.model_validate(response.json())
            else:
                raise Exception(
                    f"Warning: API returned an unexpected success code: {response.status_code}"
                )
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

    async def overwrite_ip_address(
        self, ip_address: IPAddressCreate, ip_address_id: int
    ) -> IPAddress:
        url: str = f"/api/ipam/ip-addresses/{ip_address_id}/"
        payload = ip_address.model_dump(exclude_unset=True)
        try:
            response = await self.__client.put(url, json=payload)
            response.raise_for_status()
            return IPAddress.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "IP Address not found",
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

    async def update_ip_address(
        self, ip_address: IPAddressUpdate, ip_address_id: int
    ) -> IPAddress:
        url: str = f"/api/ipam/ip-addresses/{ip_address_id}/"
        payload = ip_address.model_dump(exclude_unset=True)
        try:
            response = await self.__client.patch(url, json=payload)
            response.raise_for_status()
            return IPAddress.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "IP Address not found",
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

    async def delete_ip_address(self, ip_address_id: int) -> bool:
        url: str = f"/api/ipam/ip-addresses/{ip_address_id}/"
        try:
            response = await self.__client.delete(url)
            response.raise_for_status()
            return response.status_code == 204
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "IP Address not found",
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
