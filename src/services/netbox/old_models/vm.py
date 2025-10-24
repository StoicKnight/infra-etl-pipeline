from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class VMBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    slug: Optional[str] = ""
    display: str


class Cluster(VMBaseModel):
    name: str


class Role(VMBaseModel):
    name: str


class Site(VMBaseModel):
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


class Tag(VMBaseModel):
    name: str


class VirtualMachine(VMBaseModel):
    name: str
    role: Role
    site: Site
    primary_ip: Optional[IPAddress] = None
    description: Optional[str] = ""
    tags: List[Tag] = []
    custom_fields: Dict[str, Any] = {}
    vcpus: float
    memory: int
    disk: int
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class VMList(PaginatedResponse):
    results: List[VirtualMachine]
