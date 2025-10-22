from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from httpx import options
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

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


class DeviceStatus(str, Enum):
    OFFLINE = "offline"
    ACTIVE = "active"
    PLANNED = "planned"
    STAGED = "staged"
    FAILED = "failed"
    INVENTORY = "inventory"
    DECOMMISSIONING = "decommissioning"


class Status(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: DeviceStatus
    label: str


class Rack(DeviceBaseModel):
    name: str


class Location(DeviceBaseModel):
    name: str


class FamilyIP(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: int
    label: str


class IPAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    display: str
    family: FamilyIP
    address: str
    description: str


class Tag(DeviceBaseModel):
    name: str


class CustomFields(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cpu_cores: Optional[str] = None
    memory_gb: Optional[str] = None
    os_version: Optional[str] = None
    salt_id: Optional[str] = None
    server_Scope: Optional[str] = None
    storage_gb: Optional[str] = None
    webzilla: Optional[str] = None


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
    custom_fields: Optional[CustomFields] = None
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class DeviceList(PaginatedResponse):
    results: List[Device]


class DeviceCreate(BaseModel):
    name: str = Field(..., description="The name of the new device.")
    device_type: int = Field(..., description="The ID of the device's type.")
    role: int = Field(..., description="The ID of the device's role.")
    site: int = Field(
        ..., description="The ID of the site where the device is located."
    )
    status: DeviceStatus = Field(
        ...,
        description="The value of the device status (e.g., 'active').",
    )
    primary_ip: int = Field(..., description="The ID of the primary IP for the device")
    description: Optional[str] = None
    rack: Optional[int] = None
    location: Optional[int] = None
    oob_ip: Optional[int] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[int] = None
    role: Optional[int] = None
    site: Optional[int] = None
    status: Optional[DeviceStatus] = None
    description: Optional[str] = None
    rack: Optional[int] = None
    location: Optional[int] = None
    oob_ip: Optional[int] = None
    primary_ip: Optional[int] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None
