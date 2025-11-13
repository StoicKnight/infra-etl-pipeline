from typing import TYPE_CHECKING, AsyncGenerator, List


from src.services.xen.models import Host, PaginatedHostList

if TYPE_CHECKING:
    from src.services.xen.client import XenAPIClient


class HostsEndpoints:
    def __init__(self, client: "XenAPIClient"):
        self.__client = client
        self.__PATH = "/hosts/"

    async def list(self, **params) -> AsyncGenerator[Host, None]:
        async for host in self.__client.list(
            url=self.__PATH,
            paginated_model=PaginatedHostList,
            **params,
        ):
            yield host

    async def get_all(self) -> Host:
        fields = "id,hostname,name_label,name_description,bios_strings,$pool,power_state,enabled,cpus,memory,address,startTime,rebootRequired,version,productBrand,tags,href"

        url = self.__PATH
        return await self.__client.get(url, response_model=List[Host], fields=fields)

    async def get_items(self, host_id: str) -> Host:
        url = f"{self.__PATH}{host_id}/"
        return await self.__client.get(url, response_model=Host)
