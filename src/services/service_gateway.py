import asyncio
import logging

from src.config import Settings
from src.services.models import ServicesResponses
from src.services.netbox.client import NetBoxAPIClient
from src.services.salt.client import SaltAPIClient

log = logging.getLogger(__name__)


class ServiceGateway:
    def __init__(self, settings: Settings):
        self.__settings = settings
        self.salt_client = SaltAPIClient(
            api_url=self.__settings.salt.api_url,
            username=self.__settings.salt.username,
            password=self.__settings.salt.password,
        )
        self.netbox_client = NetBoxAPIClient(
            base_url=self.__settings.netbox.base_url.host,  # pyright: ignore
            token=self.__settings.netbox.api_token,
            verify_ssl=self.__settings.netbox.ssl,
        )

    async def get_all_service_data(self, salt_target: str = "*") -> ServicesResponses:
        log.info("Starting data fetch from all services.")

        async with self.salt_client as active_salt_client:
            async with asyncio.TaskGroup() as tg:
                salt_grains_task = tg.create_task(
                    active_salt_client.get_minion_grains(target=salt_target)
                )
        log.info("All service data fetched successfully.")

        salt_results = salt_grains_task.result()
        return ServicesResponses(
            salt=salt_results,
        )
