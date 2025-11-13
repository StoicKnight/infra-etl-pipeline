from typing import TYPE_CHECKING, AsyncGenerator

from src.services.xen.models import VirtualMachine, PaginatedVirtualMachineList

if TYPE_CHECKING:
    from src.services.xen.client import XenAPIClient


class VirtualMachinesEndpoints:
    def __init__(self, client: "XenAPIClient"):
        self.__client = client
        self.__PATH = "/vms/"

    async def list(self, **params) -> AsyncGenerator[VirtualMachine, None]:
        async for virtual_machine in self.__client.list(
            url=self.__PATH,
            paginated_model=PaginatedVirtualMachineList,
            **params,
        ):
            yield virtual_machine

    async def get_all(self, **params) -> VirtualMachine:
        url = self.__PATH
        return await self.__client.get(
            url, response_model=VirtualMachine, params=params
        )

    async def get_items(self, virtual_machine_id: str) -> VirtualMachine:
        url = f"{self.__PATH}{virtual_machine_id}/"
        return await self.__client.get(url, response_model=VirtualMachine)
