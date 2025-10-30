from typing import TYPE_CHECKING, AsyncGenerator, List, Union

from src.services.netbox.models import (
    IPAddress,
    PaginatedIPAddressList,
    PatchedIPAddressWithId,
    WritableIPAddress,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

WritableIPAddresses = Union[WritableIPAddress, List[WritableIPAddress]]
PatchedIPAddresses = Union[PatchedIPAddressWithId, List[PatchedIPAddressWithId]]
IPAddressIDs = Union[int, List[int]]


class IPAddressesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/ipam/ip-addresses/"

    async def list(self, **params) -> AsyncGenerator[IPAddress, None]:
        async for ip_address in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedIPAddressList, **params
        ):
            yield ip_address

    async def get(self, ip_address_id: int) -> IPAddress:
        url = f"{self.__PATH}{ip_address_id}/"
        return await self.__client.get(url, response_model=IPAddress)

    async def create(
        self, ip_address_data: WritableIPAddresses
    ) -> Union[IPAddress, List[IPAddress]]:
        return await self.__client.create(
            url=self.__PATH, data=ip_address_data, response_model=IPAddress
        )

    async def update(
        self, ip_address_data: PatchedIPAddresses
    ) -> Union[IPAddress, List[IPAddress]]:
        if isinstance(ip_address_data, PatchedIPAddressWithId):
            url = f"{self.__PATH}{ip_address_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=ip_address_data, response_model=IPAddress
        )

    async def delete(self, ip_address_ids: IPAddressIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=ip_address_ids)
