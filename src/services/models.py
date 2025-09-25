from pydantic import BaseModel

from .salt.models import SaltAPIResponse


class ServicesResponses(BaseModel):
    """data structure for combined results."""

    salt: SaltAPIResponse
