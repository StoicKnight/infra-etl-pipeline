import pytest
import respx
from httpx import Response

from src.services.netbox.client import NetBoxAPIClient
from src.services.netbox.models.device import Device

pytestmark = pytest.mark.asyncio  # Mark all tests in this file as async


MOCK_API_URL = "https://mock.api/api"

PAGE_1_RESPONSE = {
    "count": 2,
    "next": f"{MOCK_API_URL}/dcim/devices/?offset=1&limit=1",
    "previous": None,
    "results": [
        {
            "id": 1,
            "url": "https://mock.api/api/dcim/devices/1/",
            "name": "core-router-01",
            "status": {"value": "active", "label": "Active"},
            "site": {"id": 1, "name": "Data Center 1", "slug": "dc-1"},
            "device_type": {
                "id": 1,
                "model": "CSR1000v",
                "manufacturer": {"id": 1, "name": "Cisco", "slug": "cisco"},
            },
        }
    ],
}

PAGE_2_RESPONSE = {
    "count": 2,
    "next": None,
    "previous": f"{MOCK_API_URL}/dcim/devices/?limit=1",
    "results": [
        {
            "id": 2,
            "url": "https://mock.api/api/dcim/devices/2/",
            "name": "access-switch-01",
            "status": {"value": "active", "label": "Active"},
            "site": {"id": 2, "name": "Branch Office 5", "slug": "bo-5"},
            "device_type": {
                "id": 2,
                "model": "Catalyst 9300",
                "manufacturer": {"id": 1, "name": "Cisco", "slug": "cisco"},
            },
        }
    ],
}


@respx.mock
async def test_stream_all_devices():
    # 1. Setup the mock routes
    # Mock the request for the first page
    respx.get(f"{MOCK_API_URL}/dcim/devices/").mock(
        return_value=Response(200, json=PAGE_1_RESPONSE)
    )
    # Mock the request for the second page (using the 'next' URL)
    respx.get(f"{MOCK_API_URL}/dcim/devices/?offset=1&limit=1").mock(
        return_value=Response(200, json=PAGE_2_RESPONSE)
    )

    # 2. Initialize the client
    client = NetBoxAPIClient(base_url=MOCK_API_URL, token="fake-token")

    # 3. Call the method being tested and collect results
    streamed_devices = []
    async for device in client.devices.stream():
        streamed_devices.append(device)

    await client.close()

    # 4. Assert the results
    # Check that we received the correct number of devices
    assert len(streamed_devices) == 2

    # Check that the items are correctly parsed Pydantic models
    assert isinstance(streamed_devices[0], Device)
    assert isinstance(streamed_devices[1], Device)

    # Check the content of the devices
    assert streamed_devices[0].name == "core-router-01"
    assert streamed_devices[0].id == 1
    assert streamed_devices[0].device_type.model == "CSR1000v"

    assert streamed_devices[1].name == "access-switch-01"
    assert streamed_devices[1].id == 2
    assert streamed_devices[1].site.name == "Branch Office 5"

    # Check that both mocked API endpoints were called
    assert respx.calls.call_count == 2
