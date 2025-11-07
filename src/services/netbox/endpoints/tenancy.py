from typing import TYPE_CHECKING, AsyncGenerator, List, Union

from src.services.netbox.models import (
    PaginatedTenantList,
    PatchedTenantWithId,
    Tenant,
    WritableTenant,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

WritableTenants = Union[WritableTenant, List[WritableTenant]]
PatchedTenants = Union[PatchedTenantWithId, List[PatchedTenantWithId]]
TenantIDs = Union[int, List[int]]


class TenantsEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/tenancy/tenants/"

    async def list(self, **params) -> AsyncGenerator[Tenant, None]:
        async for tenant in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedTenantList, **params
        ):
            yield tenant

    async def get(self, tenant_id: int) -> Tenant:
        url = f"{self.__PATH}{tenant_id}/"
        return await self.__client.get(url, response_model=Tenant)

    async def create(self, tenant_data: WritableTenants) -> Union[Tenant, List[Tenant]]:
        return await self.__client.create(
            url=self.__PATH, data=tenant_data, response_model=Tenant
        )

    async def update(self, tenant_data: PatchedTenants) -> Union[Tenant, List[Tenant]]:
        if isinstance(tenant_data, PatchedTenantWithId):
            url = f"{self.__PATH}{tenant_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=tenant_data, response_model=Tenant
        )

    async def delete(self, tenant_ids: TenantIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=tenant_ids)
