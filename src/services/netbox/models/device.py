from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class DeviceBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    slug: Optional[str] = ""
    display: str


class Manufacturer(DeviceBaseModel):
    name: str
    description: str


class DeviceType(DeviceBaseModel):
    model: str
    device_count: Optional[int] = None
    manufacturer: Manufacturer


class Role(DeviceBaseModel):
    name: str


class Site(DeviceBaseModel):
    name: str


class Status(BaseModel):
    value: str
    label: str


class Rack(DeviceBaseModel):
    name: str


class Location(DeviceBaseModel):
    name: str


class FamilyIP(BaseModel):
    value: int
    label: str


class IPAddress(BaseModel):
    id: int
    url: HttpUrl
    display: str
    family: FamilyIP
    address: str
    description: str


class Tag(DeviceBaseModel):
    name: str


class Device(DeviceBaseModel):
    name: str
    device_type: DeviceType
    role: Role
    site: Site
    status: Status
    rack: Optional[Rack] = None
    location: Optional[Location] = None
    primary_ip: Optional[IPAddress] = None
    oob_ip: Optional[IPAddress] = None
    description: Optional[str] = ""
    tags: List[Tag] = []
    custom_fields: Dict[str, Any] = {}
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class DeviceList(PaginatedResponse):
    results: List[Device]
