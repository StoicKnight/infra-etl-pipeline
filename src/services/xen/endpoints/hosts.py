from typing import TYPE_CHECKING, AsyncGenerator, List


from src.services.xen.models import Host, PaginatedHostList
from src.config import settings

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
        fields = settings.xen.endpoints.hosts.fields

        url = self.__PATH
        return await self.__client.get(url, response_model=List[Host], fields=fields)

    async def get_items(self, host_id: str) -> Host:
        url = f"{self.__PATH}{host_id}/"
        return await self.__client.get(url, response_model=Host)
