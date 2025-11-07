from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel


class Grains(BaseModel):
    model_config = ConfigDict(extra="ignore")
    host: Optional[str] = None
    localhost: Optional[str] = None
    domain: Optional[str] = None
    fqdn: Optional[str] = None
    fqdn_ip4: List[str] = []
    osfinger: Optional[str] = None
    osfullname: Optional[str] = None
    kernel: Optional[str] = None
    mem_total: Optional[int] = None
    swap_total: Optional[int] = None
    num_cpus: Optional[int] = None
    productname: Optional[str] = None
    nodename: Optional[str] = None
    virtual: Optional[str] = None
    saltversion: Optional[str] = None


class MinionGrainsResponse(RootModel[Dict[str, Grains]]):
    pass
