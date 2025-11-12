from typing import TYPE_CHECKING, AsyncGenerator, List, Union

from src.services.netbox.models import (
    Device,
    PaginatedDeviceList,
    PatchedDeviceWithId,
    WritableDevice,
    DeviceType,
    PaginatedDeviceTypeList,
    PatchedDeviceTypeWithId,
    WritableDeviceType,
    Site,
    PaginatedSiteList,
    PatchedSiteWithId,
    WritableSite,
    Location,
    PaginatedLocationList,
    PatchedLocationWithId,
    WritableLocation,
    Platform,
    PaginatedPlatformList,
    PatchedPlatformWithId,
    WritablePlatform,
)

if TYPE_CHECKING:
    from src.services.netbox.client import NetBoxAPIClient

WritableDevices = Union[WritableDevice, List[WritableDevice]]
PatchedDevices = Union[PatchedDeviceWithId, List[PatchedDeviceWithId]]
DeviceIDs = Union[int, List[int]]

WritableDeviceTypes = Union[WritableDeviceType, List[WritableDeviceType]]
PatchedDeviceTypes = Union[PatchedDeviceTypeWithId, List[PatchedDeviceTypeWithId]]
DeviceTypeIDs = Union[int, List[int]]

WritableSites = Union[WritableSite, List[WritableSite]]
PatchedSites = Union[PatchedSiteWithId, List[PatchedSiteWithId]]
SiteIDs = Union[int, List[int]]

WritableLocations = Union[WritableLocation, List[WritableLocation]]
PatchedLocations = Union[PatchedLocationWithId, List[PatchedLocationWithId]]
LocationIDs = Union[int, List[int]]

WritablePlatforms = Union[WritablePlatform, List[WritablePlatform]]
PatchedPlatforms = Union[PatchedPlatformWithId, List[PatchedPlatformWithId]]
PlatformIDs = Union[int, List[int]]


class DevicesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/devices/"

    async def list(self, **params) -> AsyncGenerator[Device, None]:
        async for device in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedDeviceList, **params
        ):
            yield device

    async def get(self, device_id: int) -> Device:
        url = f"{self.__PATH}{device_id}/"
        return await self.__client.get(url, response_model=Device)

    async def create(self, device_data: WritableDevices) -> Union[Device, List[Device]]:
        return await self.__client.create(
            url=self.__PATH, data=device_data, response_model=Device
        )

    async def update(self, device_data: PatchedDevices) -> Union[Device, List[Device]]:
        if isinstance(device_data, PatchedDeviceWithId):
            url = f"{self.__PATH}{device_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=device_data, response_model=Device
        )

    async def delete(self, device_ids: DeviceIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=device_ids)


class DeviceTypesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/device-types/"

    async def list(self, **params) -> AsyncGenerator[DeviceType, None]:
        async for device_type in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedDeviceTypeList, **params
        ):
            yield device_type

    async def get(self, device_type_id: int) -> DeviceType:
        url = f"{self.__PATH}{device_type_id}/"
        return await self.__client.get(url, response_model=DeviceType)

    async def create(
        self, device_type_data: WritableDeviceTypes
    ) -> Union[DeviceType, List[DeviceType]]:
        return await self.__client.create(
            url=self.__PATH, data=device_type_data, response_model=DeviceType
        )

    async def update(
        self, device_type_data: PatchedDeviceTypes
    ) -> Union[DeviceType, List[DeviceType]]:
        if isinstance(device_type_data, PatchedDeviceTypeWithId):
            url = f"{self.__PATH}{device_type_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=device_type_data, response_model=DeviceType
        )

    async def delete(self, device_type_ids: DeviceTypeIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=device_type_ids)


class SitesEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/sites/"

    async def list(self, **params) -> AsyncGenerator[Site, None]:
        async for site in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedSiteList, **params
        ):
            yield site

    async def get(self, site_id: int) -> Site:
        url = f"{self.__PATH}{site_id}/"
        return await self.__client.get(url, response_model=Site)

    async def create(self, site_data: WritableSites) -> Union[Site, List[Site]]:
        return await self.__client.create(
            url=self.__PATH, data=site_data, response_model=Site
        )

    async def update(self, site_data: PatchedSites) -> Union[Site, List[Site]]:
        if isinstance(site_data, PatchedSiteWithId):
            url = f"{self.__PATH}{site_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(url=url, data=site_data, response_model=Site)

    async def delete(self, site_ids: SiteIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=site_ids)


class LocationsEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/locations/"

    async def list(self, **params) -> AsyncGenerator[Location, None]:
        async for location in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedLocationList, **params
        ):
            yield location

    async def get(self, location_id: int) -> Location:
        url = f"{self.__PATH}{location_id}/"
        return await self.__client.get(url, response_model=Location)

    async def create(
        self, location_data: WritableLocations
    ) -> Union[Location, List[Location]]:
        return await self.__client.create(
            url=self.__PATH, data=location_data, response_model=Location
        )

    async def update(
        self, location_data: PatchedLocations
    ) -> Union[Location, List[Location]]:
        if isinstance(location_data, PatchedLocationWithId):
            url = f"{self.__PATH}{location_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=location_data, response_model=Location
        )

    async def delete(self, location_ids: LocationIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=location_ids)


class PlatformsEndpoints:
    def __init__(self, client: "NetBoxAPIClient"):
        self.__client = client
        self.__PATH = "/api/dcim/platforms/"

    async def list(self, **params) -> AsyncGenerator[Platform, None]:
        async for platform in self.__client.list(
            url=self.__PATH, paginated_model=PaginatedPlatformList, **params
        ):
            yield platform

    async def get(self, platform_id: int) -> Platform:
        url = f"{self.__PATH}{platform_id}/"
        return await self.__client.get(url, response_model=Platform)

    async def create(
        self, platform_data: WritablePlatforms
    ) -> Union[Platform, List[Platform]]:
        return await self.__client.create(
            url=self.__PATH, data=platform_data, response_model=Platform
        )

    async def update(
        self, platform_data: PatchedPlatforms
    ) -> Union[Platform, List[Platform]]:
        if isinstance(platform_data, PatchedPlatformWithId):
            url = f"{self.__PATH}{platform_data.id}/"
        else:
            url = self.__PATH
        return await self.__client.update(
            url=url, data=platform_data, response_model=Platform
        )

    async def delete(self, platform_ids: PlatformIDs) -> bool:
        return await self.__client.delete(url=self.__PATH, data=deviceids)
