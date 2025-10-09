import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models.vm import VirtualMachine, VMList

log = logging.getLogger(__name__)


class VMEndpoints:
    def __init__(self, client: httpx.AsyncClient):
        self.__client = client

    async def list(self) -> AsyncGenerator[VirtualMachine, None]:
        next_url: Optional[str] = "/api/virtualization/virtual-machines/"
        try:
            while next_url:
                log.debug(f"Next URL: {next_url}")
                response = await self.__client.get(next_url)
                response.raise_for_status()
                vm_list = VMList.model_validate(response.json())

                for vm in vm_list.results:
                    yield vm
                if vm_list.next:
                    next_url = str(vm_list.next)
                else:
                    next_url = None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Virtual Machines list not found",
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

    async def get(self, vm_id) -> VirtualMachine:
        url: str = f"/api/virtualization/virtual-machines/{vm_id}/"
        log.debug(f"Virtual Machine URL: {url}")
        try:
            response = await self.__client.get(url)
            response.raise_for_status()
            return VirtualMachine.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "Virtual Machine not found",
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
