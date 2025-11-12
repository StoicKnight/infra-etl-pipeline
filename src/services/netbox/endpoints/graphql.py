from typing import TYPE_CHECKING, Dict, Any


if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient


class GraphQLEndpoint:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/graphql/"

    async def query(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.__client.query(url=self.__PATH, data=data)
