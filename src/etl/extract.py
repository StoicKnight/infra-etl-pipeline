import json
import logging
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
)

from pydantic import BaseModel

# from src.services.netbox.client import NetBoxAPIClient
from src.services.salt.client import SaltAPIClient
from src.services.xen.client import XenAPIClient

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

log = logging.getLogger(__name__)

InputModel = TypeVar("InputModel", bound=BaseModel)
OutputModel = TypeVar("OutputModel", bound=BaseModel)
InputData = Union[InputModel, List[InputModel]]
ItemIDs = Union[int, List[int]]


class EndpointEnum(str, Enum):
    DEVICE = "dev"
    DEVICE_TYPE = "devtypes"
    IP_ADDRESS = "ips"
    VIRTUAL_MACHINE = "vms"
    TENTANT = "tenants"
    SITE = "sites"
    LOCATION = "locations"
    PLATFORM = "platforms"
    CLUSTER = "clusters"
    GRAPHQL = "graphql"


def load_json_data(file_path: Path) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return {}


def extract_json_data(file_paths: List[Path]) -> List[Dict[str, Any]]:
    return list(map(load_json_data, file_paths))


def _get_endpoint_handler(client: "NetBoxAPIClient", endpoint: EndpointEnum) -> Any:
    handler_attribute = endpoint.value
    return getattr(client, handler_attribute)


async def list_items(
    client: "NetBoxAPIClient", endpoint: EndpointEnum, **params: Any
) -> AsyncGenerator[OutputModel, None]:
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Listing items from endpoint '{endpoint.name}' with params: {params}")
    async for item in handler.list(**params):
        yield item


async def get_item(
    client: "NetBoxAPIClient", endpoint: EndpointEnum, item_id: int
) -> OutputModel:
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Getting item with ID {item_id} from endpoint '{endpoint.name}'")
    return await handler.get(item_id)


async def create_items(
    client: "NetBoxAPIClient", endpoint: EndpointEnum, data: InputData
) -> Union[OutputModel, List[OutputModel]]:
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Creating items on endpoint '{endpoint.name}'")
    return await handler.create(data)


async def update_items(
    client: "NetBoxAPIClient", endpoint: EndpointEnum, data: InputData
) -> Union[OutputModel, List[OutputModel]]:
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Updating items on endpoint '{endpoint.name}'")
    return await handler.update(data)


async def delete_items(
    client: "NetBoxAPIClient", endpoint: EndpointEnum, item_ids: ItemIDs
) -> bool:
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Deleting item(s) with ID(s) {item_ids} from endpoint '{endpoint.name}'")
    return await handler.delete(item_ids)


async def query_graphql(
    client: "NetBoxAPIClient", query: str, variables: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    endpoint = EndpointEnum.GRAPHQL
    handler = _get_endpoint_handler(client, endpoint)
    log.info(f"Creating items on endpoint '{endpoint.name}'")
    return await handler.query(payload)
