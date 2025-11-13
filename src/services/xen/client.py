import logging
from typing import AsyncGenerator, List, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, TypeAdapter

from src.services.xen.endpoints.hosts import HostsEndpoints
from src.services.xen.endpoints.vms import VirtualMachinesEndpoints
from src.services.xen.exceptions import XenAPIError
from src.services.xen.models import BasePaginatedList


log = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
PaginatedModelType = TypeVar("PaginatedModelType", bound=BasePaginatedList)
InputData = Union[BaseModel, List[BaseModel]]


class XenAPIClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        verify_ssl: bool | str = False,
    ):
        headers = {
            "Accept": "application/json",
        }
        cookies = {"authenticationToken": token}
        self.__client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            cookies=cookies,
            timeout=40.0,
            verify=verify_ssl,
        )
        self.vms = VirtualMachinesEndpoints(self)
        self.hosts = HostsEndpoints(self)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            log.debug(f"Request: {method} {url} kwargs: {kwargs}")
            response = await self.__client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            response_text = e.response.text
            log.error(
                f"API Error: {status_code} on {method} {url}. Response: {response_text}"
            )
            if status_code == 404:
                raise XenAPIError("Object not found", status_code, response_text) from e
            if status_code in [401, 403]:
                raise XenAPIError(
                    "Authentication failed", status_code, response_text
                ) from e
            raise XenAPIError("API request failed", status_code, response_text) from e

    async def get(
        self, url: str, response_model: Type[ModelType], **params
    ) -> ModelType:
        response = await self._request("GET", url, params=params)
        adapter = TypeAdapter(response_model)
        return adapter.validate_python(response.json())

    async def list(
        self, url: str, paginated_model: Type[PaginatedModelType], **params
    ) -> AsyncGenerator[ModelType, None]:
        next_url: str | None = url
        while next_url:
            log.debug(f"Next URL: {next_url}")
            response = await self._request("GET", next_url, params=params)
            paginated_list = paginated_model.model_validate(response.json())
            for item in paginated_list.results:
                yield item
            next_url = str(paginated_list.next) if paginated_list.next else None
            params = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if not self.__client.is_closed:
            await self.__client.aclose()
            log.info("XEN API client session closed.")
