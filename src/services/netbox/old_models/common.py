from typing import Optional

from pydantic import BaseModel, HttpUrl


class PaginatedResponse(BaseModel):
    count: int
    next: Optional[HttpUrl] = None
    previous: Optional[HttpUrl] = None
