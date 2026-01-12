from typing import TYPE_CHECKING

from src.config import settings
from src.services.xen.models import VirtualMachineDevice

if TYPE_CHECKING:
    from src.services.xen.client import XenAPIClient


class VirtualMachineDevicesEndpoints:
    def __init__(self, client: "XenAPIClient"):
        self.__client = client
        self.__PATH = "/vbds/"

    async def get_all(self, vm_id: str) -> VirtualMachineDevice:
        fields = settings.xen.endpoints.vbds.fields
        filter = f"VM:{vm_id}"

        url = self.__PATH
        return await self.__client.get(
            url, response_model=list[VirtualMachineDevice], fields=fields, filter=filter
        )
