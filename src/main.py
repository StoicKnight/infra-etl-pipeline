import asyncio
import json
import logging


from src.config import settings
from src.etl.extract import EndpointEnum, create_items, query_graphql
from src.etl.transform import extract_ids_from_query
from src.logging import setup_logging
from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models import (
    DeviceStatusOptions,
    WritableDevice,
)
from src.services.netbox.queries import generate_device_creation_payload
from src.services.salt.client import SaltAPIClient

log = logging.getLogger(__name__)


async def main():
    setup_logging()
    log.debug("Main function called...")

    SALT_TARGET = "cy* and G@virtual:physical"
    SALT_TARGET = "cy111*"
    SALT_TARGET_TYPE = "compound"
    NETBOX_BASE_URL = str(settings.netbox.base_url)
    NETBOX_API_TOKEN = settings.netbox.api_token
    VERIFY_SSL = settings.netbox.ssl
    devices_to_create = []
    query_ids_results = {}
    minion_data = None

    log.info("Initializing NetBox API client.")
    async with NetBoxAPIClient(
        base_url=NETBOX_BASE_URL, token=NETBOX_API_TOKEN, verify_ssl=VERIFY_SSL
    ) as netbox_client:
        log.info("Initializing Salt API client.")
        async with await SaltAPIClient.create(
            api_url=settings.salt.api_url,
            username=settings.salt.username,
            password=settings.salt.password,
        ) as salt_client:
            try:
                minion_data = await salt_client.get_minion_grains(
                    SALT_TARGET, SALT_TARGET_TYPE
                )
                minion_count = len(minion_data.root)
                log.info(f"Salt returned data for {minion_count} minions.")

                # query, variables = generate_device_creation_payload(
                #     device_type="r740xd",
                #     site="hfm",
                #     location="7",
                #     platform="2022",
                #     cluster="039",
                #     tenant="infra",
                #     role="mt4 trading",
                # )
                # log.info("Get list of available device types.")
                # query_ids_results = await query_graphql(
                #     client=netbox_client, query=query, variables=variables
                # )
                # create_devices_ids = extract_ids_from_query(query_ids_results)

                log.info("Creating WritableDevice object to push to NetBox")
                if minion_data.root:
                    for minion_id, grains in minion_data.root.items():
                        if grains.virtual == "physical":
                            query, variables = generate_device_creation_payload(
                                device_type=str(grains.productname),
                                site="hfm",
                                location="7",
                                platform="2022",
                                cluster="039",
                                tenant="infra",
                                role="mt4 trading",
                            )
                            log.info("Get list of available device types.")
                            query_ids_results = await query_graphql(
                                client=netbox_client, query=query, variables=variables
                            )
                            create_devices_ids = extract_ids_from_query(
                                query_ids_results
                            )
                            devices_to_create.append(
                                WritableDevice(
                                    name=minion_id,
                                    device_type=create_devices_ids.get("deviceType", 0),
                                    site=create_devices_ids.get("site", 0),
                                    location=create_devices_ids.get("location", 0),
                                    platform=create_devices_ids.get("platform", 0),
                                    cluster=create_devices_ids.get("cluster", 0),
                                    tenant=create_devices_ids.get("tenant", 0),
                                    role=create_devices_ids.get("role", 0),
                                    status=DeviceStatusOptions.ACTIVE,
                                    description=grains.virtual,
                                )
                            )
                    log.info("Starting device creation...")
                    created_devices = await create_items(
                        netbox_client, EndpointEnum.DEVICE, data=devices_to_create
                    )
                    log.info(f"SUCCESS: Created {len(created_devices)} devices.")
            except Exception:
                log.exception("An unexpected error occurred.")
            finally:
                log.info("Closing API clients")
                await salt_client.close()
                await netbox_client.close()


if __name__ == "__main__":
    asyncio.run(main())
