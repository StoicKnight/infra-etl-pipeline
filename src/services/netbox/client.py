import logging
from typing import AsyncGenerator, List, Type, TypeVar, Union

import httpx
from pydantic import BaseModel

from src.services.netbox.endpoints.dcim import DevicesEndpoints
from src.services.netbox.endpoints.ipam import IPAddressesEndpoints
from src.services.netbox.endpoints.virtualization import VirtualMachinesEndpoints
from src.services.netbox.exceptions import NetBoxAPIError
from src.services.netbox.models import BasePaginatedList

log = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
PaginatedModelType = TypeVar("PaginatedModelType", bound=BasePaginatedList)
InputData = Union[BaseModel, List[BaseModel]]


class NetBoxAPIClient:
    def __init__(self, base_url: str, token: str, verify_ssl: bool | str = True):
        headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json",
        }
        self.__client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=20.0,
            verify=verify_ssl,
        )
        self.dev = DevicesEndpoints(self)
        self.ips = IPAddressesEndpoints(self)
        self.vms = VirtualMachinesEndpoints(self)

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
                raise NetBoxAPIError(
                    "Object not found", status_code, response_text
                ) from e
            if status_code in [401, 403]:
                raise NetBoxAPIError(
                    "Authentication failed", status_code, response_text
                ) from e
            raise NetBoxAPIError(
                "API request failed", status_code, response_text
            ) from e

    async def get(self, url: str, response_model: Type[ModelType]) -> ModelType:
        response = await self._request("GET", url)
        return response_model.model_validate(response.json())

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

    async def create(
        self, url: str, data: InputData, response_model: Type[ModelType]
    ) -> Union[ModelType, List[ModelType]]:
        if isinstance(data, list):
            payload = [
                item.model_dump(exclude_unset=True, by_alias=True) for item in data
            ]
        else:
            payload = data.model_dump(exclude_unset=True, by_alias=True)
        response = await self._request("POST", url, json=payload)
        json_response = response.json()
        if isinstance(json_response, list):
            return [response_model.model_validate(item) for item in json_response]
        else:
            return response_model.model_validate(json_response)

    async def update(
        self, url: str, data: InputData, response_model: Type[ModelType]
    ) -> Union[ModelType, List[ModelType]]:
        if isinstance(data, list):
            payload = [
                item.model_dump(exclude_unset=True, by_alias=True) for item in data
            ]
        else:
            payload = data.model_dump(exclude_unset=True, by_alias=True)
        response = await self._request("PATCH", url, json=payload)
        json_response = response.json()
        if isinstance(json_response, list):
            return [response_model.model_validate(item) for item in json_response]
        else:
            return response_model.model_validate(json_response)

    async def delete(self, url: str, data: Union[int, List[int]]) -> bool:
        if isinstance(data, list):
            payload = [{"id": obj_id} for obj_id in data]
            response = await self._request("DELETE", url, json=payload)
        else:
            delete_url = f"{url}{data}/"
            response = await self._request("DELETE", delete_url)
        return response.status_code == 204

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if not self.__client.is_closed:
            await self.__client.aclose()
            log.info("NetBox API client session closed.")
