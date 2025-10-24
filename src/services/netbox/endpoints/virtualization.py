import logging
from typing import AsyncGenerator, Optional

import httpx

from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models import (
    PaginatedVirtualMachineList,
    PatchedVirtualMachine,
    VirtualMachine,
    WritableVirtualMachine,
)

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
                vm_list = PaginatedVirtualMachineList.model_validate(response.json())

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

    async def create_vm(
        self, virtual_machine: WritableVirtualMachine
    ) -> Optional[VirtualMachine]:
        url: str = "/api/virtualization/virtual-machines/"
        payload = virtual_machine.model_dump(exclude_unset=True)
        try:
            response = await self.__client.post(url, json=payload)
            response.raise_for_status()
            if response.status_code == 201:
                log.info("VM created successfully (Status: 201 Created).")
                return VirtualMachine.model_validate(response.json())
            else:
                raise Exception(
                    f"Warning: API returned an unexpected success code: {response.status_code}"
                )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "VM not found",
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

    async def overwrite_vm(
        self, virtual_machine: WritableVirtualMachine, vm_id: int
    ) -> VirtualMachine:
        url: str = f"/api/virtualization/virtual-machines/{vm_id}/"
        payload = virtual_machine.model_dump(exclude_unset=True)
        try:
            response = await self.__client.put(url, json=payload)
            response.raise_for_status()
            return VirtualMachine.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "VM not found",
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

    async def update_vm(
        self, virtual_machine: PatchedVirtualMachine, vm_id: int
    ) -> VirtualMachine:
        url: str = f"/api/virtualization/virtual-machines/{vm_id}/"
        payload = virtual_machine.model_dump(exclude_unset=True)
        try:
            response = await self.__client.patch(url, json=payload)
            response.raise_for_status()
            return VirtualMachine.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "VM not found",
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

    async def delete_vm(self, vm_id: int) -> bool:
        url: str = f"/api/virtualization/virtual-machines/{vm_id}/"
        try:
            response = await self.__client.delete(url)
            response.raise_for_status()
            return response.status_code == 204
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NetBoxAPIError(
                    "VM not found",
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
