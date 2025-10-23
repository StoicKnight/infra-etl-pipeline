import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models.tenant import (
    Tenant,
    TenantCreate,
    TenantList,
    TenantUpdate,
)

log = logging.getLogger(__name__)


class TenancyEndpoints:
    def __init__(self, client: httpx.AsyncClient):
        self.__client = client

    async def list(self) -> AsyncGenerator[Tenant, None]:
        next_url: Optional[str] = "/api/tenancy/tenants/"
        try:
            while next_url:
                log.debug(f"Next URL: {next_url}")
                response = await self.__client.get(next_url)
                response.raise_for_status()
                tenant_list = TenantList.model_validate(response.json())

                for tenant in tenant_list.results:
                    yield tenant
                if tenant_list.next:
                    next_url = str(tenant_list.next)
                else:
                    next_url = None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenants list not found",
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

    async def get(self, tenant_id) -> Tenant:
        url: str = f"/api/tenancy/tenants/{tenant_id}/"
        try:
            response = await self.__client.get(url)
            response.raise_for_status()
            return Tenant.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenant not found",
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

    async def create_tenant(self, tenant: TenantCreate) -> Optional[Tenant]:
        url: str = "/api/tenancy/tenants/"
        payload = tenant.model_dump(exclude_unset=True)
        try:
            response = await self.__client.post(url, json=payload)
            response.raise_for_status()
            if response.status_code == 201:
                log.info("Tenant created successfully (Status: 201 Created).")
                return Tenant.model_validate(response.json())
            else:
                raise Exception(
                    f"Warning: API returned an unexpected success code: {response.status_code}"
                )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenant not found",
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

    async def overwrite_tenant(self, tenant: TenantCreate, tenant_id: int) -> Tenant:
        url: str = f"/api/tenancy/tenants/{tenant_id}/"
        payload = tenant.model_dump(exclude_unset=True)
        try:
            response = await self.__client.put(url, json=payload)
            response.raise_for_status()
            return Tenant.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenant not found",
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

    async def update_tenant(self, tenant: TenantUpdate, tenant_id: int) -> Tenant:
        url: str = f"/api/tenancy/tenants/{tenant_id}/"
        payload = tenant.model_dump(exclude_unset=True)
        try:
            response = await self.__client.patch(url, json=payload)
            response.raise_for_status()
            return Tenant.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenant not found",
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

    async def delete_tenant(self, tenant_id: int) -> bool:
        url: str = f"/api/tenancy/tenants/{tenant_id}/"
        try:
            response = await self.__client.delete(url)
            response.raise_for_status()
            return response.status_code == 204
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Tenant not found",
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
