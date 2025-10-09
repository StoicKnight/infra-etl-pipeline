from pydantic import BaseModel

from src.services.salt.models import SaltAPIResponse


class ServicesResponses(BaseModel):
    salt: SaltAPIResponse
