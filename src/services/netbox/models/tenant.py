from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.services.netbox.models.common import PaginatedResponse


class Tenant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: HttpUrl
    name: str = ""
    display: str
    ipaddress_count: Optional[int] = 0
    slug: Optional[str] = ""
    custom_fields: Dict[str, Any] = {}
    created: Optional[datetime] = None
    last_updated: Optional[datetime] = None


class TenantList(PaginatedResponse):
    results: List[Tenant]
