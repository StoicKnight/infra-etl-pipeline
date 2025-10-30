from typing import TYPE_CHECKING, AsyncGenerator, List, Union

from src.services.netbox.models import (
    Device,
    PaginatedDeviceList,
    PatchedDeviceWithId,
    WritableDevice,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

WritableDevices = Union[WritableDevice, List[WritableDevice]]
PatchedDevices = Union[PatchedDeviceWithId, List[PatchedDeviceWithId]]
DeviceIDs = Union[int, List[int]]


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

    async def create(self, device_data: WritableDevices) -> Union[Device, List[Device]]:
        return await self.__client.create(
            url=self.__PATH, data=device_data, response_model=Device
        )

    async def update(self, device_data: PatchedDevices) -> Union[Device, List[Device]]:
        if isinstance(device_data, PatchedDeviceWithId):
            url = f"{self.__PATH}{device_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=device_data, response_model=Device
        )

    async def delete(self, device_ids: DeviceIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=device_ids)
