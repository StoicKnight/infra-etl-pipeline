from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class Tenant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    name: str = ""
    slug: str = ""
    display: str
    ipaddress_count: Optional[int] = 0
    custom_fields: Dict[str, Any] = {}
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class TenantList(PaginatedResponse):
    results: List[Tenant]


class TenantCreate(BaseModel):
    name: str = Field(..., description="The name of the tenant.")
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None
