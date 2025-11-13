from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import (
    field_validator,
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)
import datetime


class VirtualMachinePowerStateOptions(str, Enum):
    HALTED = "Halted"
    PAUSED = "Paused"
    RUNNING = "Running"
    SUSPENDED = "Suspended"


class HostPowerStateOptions(str, Enum):
    HALTED = "Halted"
    RUNNING = "Running"
    UNKNOWN = "Unknown"


class Cpus(BaseModel):
    cores: int
    sockets: int | None = None
    max: int | None = None


class Memory(BaseModel):
    usage: int
    total: int | None = None
    static: List[int] | None = None
    dynamic: List[int] | None = None
    size: int


class BiosStrings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    system_manufacturer: str = Field(alias="system-manufacturer")
    system_product_name: str = Field(alias="system-product-name")
    system_serial_number: str = Field(alias="system-serial-number")


class IPAddresses(BaseModel):
    ipv4: str | None = Field(default=None, alias="0/ipv4/0")
    ipv6: str | None = Field(default=None, alias="0/ipv6/0")


class OSVersion(BaseModel):
    name: str
    distro: str
    major: str
    minor: str


class Host(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    hostname: str
    name_label: str
    name_description: str
    bios_strings: BiosStrings
    pool: str = Field(alias="$pool")
    power_state: HostPowerStateOptions
    enabled: bool
    cpus: Cpus
    memory: Memory
    address: str
    startTime: str
    rebootRequired: bool
    version: str
    productBrand: str
    tags: List[str]
    href: str

    @field_validator("startTime", mode="before")
    @classmethod
    def format_timestamp(cls, value: int) -> str:
        dt_object = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return dt_object.isoformat()


class VirtualMachine(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name_label: str
    name_description: str
    affinityHost: str
    pool: str
    power_state: VirtualMachinePowerStateOptions
    CPUs: Cpus
    memory: Memory
    addresses: IPAddresses
    auto_poweron: bool
    isNestedVirtEnabled: bool
    installTime: str
    startTime: str
    mainIpAddress: str
    managementAgentDetected: bool
    os_version: OSVersion
    snapshots: List[str]
    tags: List[str]
    href: str

    @field_validator("startTime", "installTime", mode="before")
    @classmethod
    def format_timestamp(cls, value: int) -> str:
        dt_object = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return dt_object.isoformat()


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
PaginatedHostList = BasePaginatedList[Host]
