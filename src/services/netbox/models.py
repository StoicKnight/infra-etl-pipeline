from enum import Enum
from typing import Any, Generic, Optional, TypeVar, Union

from pydantic import (
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    confloat,
    conint,
    constr,
)

# --- Enums ---


class DeviceStatusOptions(str, Enum):
    OFFLINE = "offline"
    ACTIVE = "active"
    PLANNED = "planned"
    STAGED = "staged"
    FAILED = "failed"
    INVENTORY = "inventory"
    DECOMMISSIONING = "decommissioning"


class IPStatusOptions(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"
    DHCP = "dhcp"
    SLAAC = "slaac"


class VMStatusOptions(str, Enum):
    OFFLINE = "offline"
    ACTIVE = "active"
    PLANNED = "planned"
    STAGED = "staged"
    FAILED = "failed"
    DECOMMISSIONING = "decommissioning"
    PAUSED = "paused"


class IPRoleValue(str, Enum):
    LOOPBACK = "loopback"
    SECONDARY = "secondary"
    ANYCAST = "anycast"
    VIP = "vip"
    VRRP = "vrrp"
    HSRP = "hsrp"
    GLBP = "glbp"
    CARP = "carp"
    EMPTY = ""


# --- Custom Fields and Nested Models ---


class CustomFields(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cpu_cores: Optional[int] = Field(None, description="Number of CPU cores")
    memory_gb: Optional[int] = Field(None, description="Memory in gigabytes")
    salt_id: Optional[str] = Field(None, description="SaltStack ID")
    server_scope: Optional[str] = Field(None, description="Scope of the server")
    storage_gb: Optional[int] = Field(None, description="Storage in gigabytes")
    webzilla: Optional[str] = Field(None, description="Webzilla identifier")


class DeviceStatus(BaseModel):
    value: DeviceStatusOptions
    label: str


class IPStatus(BaseModel):
    value: IPStatusOptions
    label: str


class IPFamily(BaseModel):
    value: Optional[Union[int, str]] = Field(
        None, description="* `4` - IPv4\n* `6` - IPv6"
    )
    label: Optional[str] = None


class IPRole(BaseModel):
    value: Optional[IPRoleValue] = None
    label: Optional[str] = None


class NestedTag(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-\w]+$", max_length=100)
    color: Optional[constr(pattern=r"^[0-9a-f]{6}$", max_length=6)] = None


class NestedTagRequest(BaseModel):
    name: constr(min_length=1, max_length=100)
    slug: constr(pattern=r"^[-\w]+$", min_length=1, max_length=100)
    color: Optional[constr(pattern=r"^[0-9a-f]{6}$", min_length=1, max_length=6)] = None


# --- Brief Models ---


class BriefManufacturer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefDeviceType(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    manufacturer: BriefManufacturer
    model: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefDeviceRole(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefTenant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefPlatform(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefSite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100) = Field(..., description="Full name of the site")
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefIPAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    family: IPFamily
    address: str
    description: Optional[constr(max_length=200)] = None


class BriefLocation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    slug: constr(pattern=r"^[-a-zA-Z0-9_]+$", max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefRack(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefCluster(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    description: Optional[constr(max_length=200)] = None


class BriefDevice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: Optional[constr(max_length=64)] = None
    description: Optional[constr(max_length=200)] = None


class BriefVRF(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=100)
    description: Optional[constr(max_length=200)] = None


# --- Full Models ---


class Device(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: Optional[constr(max_length=64)] = None
    device_type: BriefDeviceType
    role: BriefDeviceRole
    tenant: Optional[BriefTenant] = None
    platform: Optional[BriefPlatform] = None
    serial: Optional[constr(max_length=50)] = Field(
        None,
        description="Chassis serial number, assigned by the manufacturer",
        title="Serial number",
    )
    site: BriefSite
    location: Optional[BriefLocation] = None
    rack: Optional[BriefRack] = None
    status: Optional[DeviceStatus] = None
    primary_ip: Optional[BriefIPAddress]
    primary_ip4: Optional[BriefIPAddress] = None
    oob_ip: Optional[BriefIPAddress] = None
    cluster: Optional[BriefCluster] = None
    description: Optional[constr(max_length=200)] = None
    tags: Optional[list[NestedTag]] = None
    custom_fields: Optional[dict[str, Any]] = None
    created: AwareDatetime
    last_updated: AwareDatetime


class IPAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    family: IPFamily
    address: str
    vrf: Optional[BriefVRF] = None
    tenant: Optional[BriefTenant] = None
    status: Optional[IPStatus] = None
    role: Optional[IPRole] = None
    dns_name: Optional[
        constr(pattern=r"^([0-9A-Za-z_-]+|\*)(\.[0-9A-Za-z_-]+)*\.?$", max_length=255)
    ] = Field(None, description="Hostname or FQDN (not case-sensitive)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTag]] = None
    custom_fields: Optional[dict[str, Any]] = None
    created: AwareDatetime
    last_updated: AwareDatetime


class VirtualMachine(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    url: AnyUrl
    display: str
    name: constr(max_length=64)
    status: Optional[DeviceStatus] = None
    site: Optional[BriefSite] = None
    cluster: Optional[BriefCluster] = None
    device: Optional[BriefDevice] = None
    role: Optional[BriefDeviceRole] = None
    tenant: Optional[BriefTenant] = None
    platform: Optional[BriefPlatform] = None
    primary_ip: BriefIPAddress
    primary_ip4: Optional[BriefIPAddress] = None
    vcpus: Optional[confloat(ge=0.01, lt=10000.0)] = None
    memory: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Memory (MB)")
    disk: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Disk (GB)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTag]] = None
    custom_fields: Optional[dict[str, Any]] = None
    created: AwareDatetime
    last_updated: AwareDatetime


# --- Paginated List Models ---
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


PaginatedDeviceList = BasePaginatedList[Device]
PaginatedIPAddressList = BasePaginatedList[IPAddress]
PaginatedVirtualMachineList = BasePaginatedList[VirtualMachine]


# --- Writable and Request Models ---


class WritableDevice(BaseModel):
    name: Optional[constr(max_length=64)] = None
    device_type: int
    role: int
    tenant: Optional[int] = None
    platform: Optional[int] = None
    serial: Optional[constr(max_length=50)] = None
    site: int
    location: Optional[int] = None
    rack: Optional[int] = None
    position: Optional[confloat(ge=0.5, lt=1000.0)] = None
    status: Optional[DeviceStatusOptions] = None
    primary_ip4: Optional[int] = None
    oob_ip: Optional[int] = None
    cluster: Optional[int] = None
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None


class PatchedDevice(BaseModel):
    name: Optional[constr(max_length=64)] = None
    device_type: Optional[int] = None
    role: Optional[int] = None
    tenant: Optional[int] = None
    platform: Optional[int] = None
    serial: Optional[constr(max_length=50)] = Field(
        None,
        description="Chassis serial number, assigned by the manufacturer",
        title="Serial number",
    )
    site: Optional[int] = None
    location: Optional[int] = None
    rack: Optional[int] = None
    position: Optional[confloat(ge=0.5, lt=1000.0)] = Field(None, title="Position (U)")
    status: Optional[DeviceStatusOptions] = None
    primary_ip4: Optional[int] = None
    oob_ip: Optional[int] = None
    cluster: Optional[int] = None
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None


class WritableIPAddress(BaseModel):
    address: constr(min_length=1)
    vrf: Optional[int] = None
    tenant: Optional[int] = None
    status: Optional[IPStatusOptions] = None
    role: Optional[IPRoleValue] = None
    dns_name: Optional[
        constr(pattern=r"^([0-9A-Za-z_-]+|\*)(\.[0-9A-Za-z_-]+)*\.?$", max_length=255)
    ] = Field(None, description="Hostname or FQDN (not case-sensitive)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None


class PatchedIPAddress(BaseModel):
    address: Optional[constr(min_length=1)] = None
    vrf: Optional[int] = None
    tenant: Optional[int] = None
    status: Optional[IPStatusOptions] = None
    role: Optional[IPRoleValue] = None
    dns_name: Optional[
        constr(pattern=r"^([0-9A-Za-z_-]+|\*)(\.[0-9A-Za-z_-]+)*\.?$", max_length=255)
    ] = Field(None, description="Hostname or FQDN (not case-sensitive)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None


class WritableVirtualMachine(BaseModel):
    name: constr(min_length=1, max_length=64)
    status: Optional[VMStatusOptions] = None
    site: Optional[int] = None
    cluster: Optional[int] = None
    device: Optional[int] = None
    role: Optional[int] = None
    tenant: Optional[int] = None
    platform: Optional[int] = None
    primary_ip4: Optional[int] = None
    vcpus: Optional[confloat(ge=0.01, lt=10000.0)] = None
    memory: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Memory (MB)")
    disk: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Disk (GB)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None


class PatchedVirtualMachine(BaseModel):
    name: Optional[constr(min_length=1, max_length=64)] = None
    status: Optional[VMStatusOptions] = None
    site: Optional[int] = None
    cluster: Optional[int] = None
    device: Optional[int] = None
    role: Optional[int] = None
    tenant: Optional[int] = None
    platform: Optional[int] = None
    primary_ip4: Optional[int] = None
    vcpus: Optional[confloat(ge=0.01, lt=10000.0)] = None
    memory: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Memory (MB)")
    disk: Optional[conint(ge=0, le=2147483647)] = Field(None, title="Disk (GB)")
    description: Optional[constr(max_length=200)] = None
    comments: Optional[str] = None
    tags: Optional[list[NestedTagRequest]] = None
    custom_fields: Optional[dict[str, Any]] = None
