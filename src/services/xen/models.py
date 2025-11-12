from typing import Generic, Optional, TypeVar

from pydantic import (
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class VirtualMachine(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    label: str
    host: str
    poolId: str
    status: str
    href: AnyUrl


T = TypeVar("T")


class BasePaginatedList(BaseModel, Generic[T]):
    count: int = Field(..., examples=[123])
    next: Optional[HttpUrl] = Field(
        None, examples=["http://0.0.0.0:8000/dcim/devices/?offset=400&limit=100"]
    )
    previous: Optional[AnyUrl] = Field(
        None, examples=["http://0.0.0.0:8000/dcim/devices/?offset=400&limit=100"]
    )
    results: list[T]


PaginatedVirtualMachineList = BasePaginatedList[VirtualMachine]


class WritableVirtualMachine(BaseModel):
    label: str
    host: str
    poolId: str
    status: str
    href: AnyUrl


class PatchedVirtualMachine(BaseModel):
    label: str
    host: str
    poolId: str
    status: str
    href: AnyUrl


class PatchedVirtualMachineWithId(PatchedVirtualMachine):
    id: int
