import asyncio
import logging

from ..config import Settings
from .models import ServicesResponses
from .salt.client import SaltAPIClient

log = logging.getLogger(__name__)


class ServiceGateway:
    """
    Gateway to all external API services.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self.salt_client = SaltAPIClient(
            api_url=self._settings.salt.api_url,
            username=self._settings.salt.username,
            password=self._settings.salt.password,
        )

    async def get_all_service_data(self, salt_target: str = "*") -> ServicesResponses:
        """
        Orchestrates concurrent calls to all services.
        """
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
