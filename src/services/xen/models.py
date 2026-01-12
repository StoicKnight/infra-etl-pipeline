from enum import Enum
import logging
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


log = logging.getLogger(__name__)


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
    cores: int | None = None
    sockets: int | None = None
    max: int | None = None


class Memory(BaseModel):
    usage: int | None = None
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
    model_config = ConfigDict(extra="allow")


class OSVersion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None = None
    distro: str | None = None
    major: str | None = None
    minor: str | None = None


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
    name_description: str | None = None
    affinityHost: str | None = None
    pool: str | None = Field(default=None, alias="$pool")
    container: str | None = Field(default=None, alias="$container")
    power_state: VirtualMachinePowerStateOptions | None = None
    CPUs: Cpus | None = None
    memory: Memory | None = None
    addresses: dict[str, str] | None = None
    auto_poweron: bool | None = None
    isNestedVirtEnabled: bool | None = None
    installTime: str | None = None
    startTime: str | None = None
    mainIpAddress: str | None = None
    managementAgentDetected: bool | None = None
    os_version: OSVersion | None = None
    snapshots: List[str] | None = None
    tags: List[str] | None = None
    href: str | None = None

    @field_validator("startTime", "installTime", mode="before")
    @classmethod
    def format_timestamp(cls, value: int) -> str:
        if not isinstance(value, int) or value is None:
            # log.warning("The timestamp is not integer or empty")
            return ""
        dt_object = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return dt_object.isoformat()


class VirtualDisk(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name_label: str
    name_description: str
    size: int
    pool: str | None = Field(default=None, alias="$pool")
    missing: bool
    snapshots: List[str]
    tags: List[str]
    href: str


class VirtualMachineDevice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    vm: str = Field(alias="VM")
    read_only: bool
    is_cd_drive: bool
    attached: bool
    bootable: bool
    device: str | None = None
    vdi: str | None = Field(default=None, alias="VDI")
    pool: str = Field(alias="$pool")
    href: str


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
