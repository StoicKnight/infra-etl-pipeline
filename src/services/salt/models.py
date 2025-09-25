from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel


class Grains(BaseModel):
    """
    Mode for single minion's grains.

    Dynamic dictionary-like access to all grains and
    type-safe properties for common, default grains.
    """

    osfinger: Optional[str] = None
    kernel: Optional[str] = None
    mem_total: Optional[int] = None
    virtual: Optional[str] = None
    swap_total: Optional[int] = None
    saltversion: Optional[str] = None
    fqdn_ip4: List[str] = []
    num_cpus: Optional[int] = None

    model_config = ConfigDict(extra="allow")

    # @property
    # def osfinger(self) -> Optional[str]:
    #     return self.model_extra.get("osfinger") if self.model_extra else None
    #
    # @property
    # def kernel(self) -> Optional[str]:
    #     return self.model_extra.get("kernel") if self.model_extra else None
    #
    # @property
    # def mem_total(self) -> Optional[int]:
    #     return self.model_extra.get("mem_total") if self.model_extra else None
    #
    # @property
    # def virtual(self) -> Optional[str]:
    #     return self.model_extra.get("virtual") if self.model_extra else None
    #
    # @property
    # def swap_total(self) -> Optional[int]:
    #     return self.model_extra.get("swap_total") if self.model_extra else None
    #
    # @property
    # def saltversion(self) -> Optional[str]:
    #     return self.model_extra.get("saltversion") if self.model_extra else None
    #
    # @property
    # def fqdn_ip4(self) -> List[str]:
    #     return self.model_extra.get("fqdn_ip4", []) if self.model_extra else []
    #
    # @property
    # def num_cpus(self) -> Optional[int]:
    #     return self.model_extra.get("num_cpus") if self.model_extra else None
    #
    # def get(self, key: str, default: Any = None) -> Any:
    #     """Access grain by key."""
    #     return self.model_extra.get(key, default) if self.model_extra else default


class MinionGrainsResponse(RootModel):
    """
    Top-level dictionary mapping minion IDs to their Grains.
    """

    root: Dict[str, Grains]


class SaltAPIResponse(BaseModel):
    """JSON response from a Salt API command."""

    return_data: List[MinionGrainsResponse] = Field(alias="return")
