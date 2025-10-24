from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class SiteBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    slug: Optional[str] = ""
    display: str


class SiteStatus(str, Enum):
    PLANNED = "planned"
    STAGING = "staging"
    ACTIVE = "active"
    DECOMMISSIONING = "decommissioning"
    RETIRED = "retired"


class Status(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: SiteStatus
    label: str


class Region(SiteBaseModel):
    name: str


class Site(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    name: str
    slug: str
    display: str
    status: Status
    custom_fields: Dict[str, Any] = {}
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class SiteList(PaginatedResponse):
    results: List[Site]


class SiteCreate(BaseModel):
    name: str = Field(..., description="The name of the tenant.")
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None
