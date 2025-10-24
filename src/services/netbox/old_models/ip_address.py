from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class IPAddressBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    slug: Optional[str] = ""
    display: str


class FamilyIP(BaseModel):
    value: int
    label: str


class Tenant(IPAddressBaseModel):
    name: str
    description: str


class IPStatus(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"
    DHCP = "dhcp"
    SLAAC = "slaac"


class Status(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: IPStatus
    label: str


class Tag(IPAddressBaseModel):
    name: str


class IPAddress(IPAddressBaseModel):
    family: FamilyIP
    address: str
    tenant: Tenant
    status: Status
    description: Optional[str] = ""
    tags: List[Tag] = []
    custom_fields: Dict[str, Any] = {}
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class IPAddressList(PaginatedResponse):
    results: List[IPAddress]


class IPAddressCreate(BaseModel):
    address: str = Field(..., description="The IP address to be created.")
    tenant: int = Field(..., description="The tenant ID of the IP address.")
    status: IPStatus = Field(
        ..., description="The status of the IP address (e.g., 'active')."
    )
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class IPAddressUpdate(BaseModel):
    address: Optional[str] = None
    tenant: Optional[int] = None
    status: Optional[IPStatus] = None
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None
