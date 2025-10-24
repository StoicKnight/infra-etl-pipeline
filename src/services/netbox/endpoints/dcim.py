import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models import (
    Device,
    PaginatedDeviceList,
    PatchedDevice,
    WritableDevice,
)

log = logging.getLogger(__name__)


class DevicesEndpoints:
    def __init__(self, client: httpx.AsyncClient):
        self.__client = client

    async def list(self) -> AsyncGenerator[Device, None]:
        next_url: Optional[str] = "/api/dcim/devices/"
        try:
            while next_url:
                log.debug(f"Next URL: {next_url}")
                response = await self.__client.get(next_url)
                response.raise_for_status()
                device_list = PaginatedDeviceList.model_validate(response.json())

                for device in device_list.results:
                    yield device
                if device_list.next:
                    next_url = str(device_list.next)
                else:
                    next_url = None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device list not found",
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

    async def get(self, device_id) -> Device:
        url: str = f"/api/dcim/devices/{device_id}/"
        log.debug(f"Device URL: {url}")
        try:
            response = await self.__client.get(url)
            response.raise_for_status()
            return Device.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device not found",
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

    async def create_device(self, device: WritableDevice) -> Optional[Device]:
        url: str = "/api/dcim/devices/"
        payload = device.model_dump(exclude_unset=True)
        try:
            response = await self.__client.post(url, json=payload)
            response.raise_for_status()
            if response.status_code == 201:
                log.info("Device created successfully (Status: 201 Created).")
                return Device.model_validate(response.json())
            else:
                raise Exception(
                    f"Warning: API returned an unexpected success code: {response.status_code}"
                )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device not found",
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

    async def overwrite_device(self, device: WritableDevice, device_id: int) -> Device:
        url: str = f"/api/dcim/devices/{device_id}/"
        payload = device.model_dump(exclude_unset=True)
        try:
            response = await self.__client.put(url, json=payload)
            response.raise_for_status()
            return Device.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device not found",
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

    async def update_device(self, device: PatchedDevice, device_id: int) -> Device:
        url: str = f"/api/dcim/devices/{device_id}/"
        payload = device.model_dump(exclude_unset=True)
        try:
            response = await self.__client.patch(url, json=payload)
            response.raise_for_status()
            return Device.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device not found",
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

    async def delete_device(self, device_id: int) -> bool:
        url: str = f"/api/dcim/devices/{device_id}/"
        try:
            response = await self.__client.delete(url)
            response.raise_for_status()
            return response.status_code == 204
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Device not found",
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
