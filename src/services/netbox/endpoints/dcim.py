from typing import TYPE_CHECKING, AsyncGenerator

from src.services.netbox.models import (
    Device,
    PaginatedDeviceList,
    PatchedDevice,
    WritableDevice,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient


class DevicesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/devices/"

    async def list(self, **params) -> AsyncGenerator[Device, None]:
        async for device in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedDeviceList, **params
        ):
            yield device

    async def get(self, device_id: int) -> Device:
        url = f"{self.__PATH}{device_id}/"
        return await self.__client.get(url, response_model=Device)

    async def create(self, device_data: WritableDevice) -> Device:
        return await self.__client.create(
            url=self.__PATH, data=device_data, response_model=Device
        )

    async def update(self, device_id: int, device_data: PatchedDevice) -> Device:
        url = f"{self.__PATH}{device_id}/"
        return await self.__client.update(
            url=url, data=device_data, response_model=Device
        )

    async def delete(self, device_id: int) -> bool:
        url = f"{self.__PATH}{device_id}/"
        return await self.__client.delete(url)
