from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

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


class Status(BaseModel):
    value: str
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
