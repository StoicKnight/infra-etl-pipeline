from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel


class Grains(BaseModel):
    model_config = ConfigDict(extra="ignore")
    host: Optional[str] = None
    osfinger: Optional[str] = None
    kernel: Optional[str] = None
    mem_total: Optional[int] = None
    virtual: Optional[str] = None
    swap_total: Optional[int] = None
    saltversion: Optional[str] = None
    fqdn_ip4: List[str] = []
    num_cpus: Optional[int] = None


class MinionGrainsResponse(RootModel[Dict[str, Grains]]):
    pass
