from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, HttpUrl


class XenAPIConfig(BaseModel):
    base_url: HttpUrl
    token: str


class XenDatacenterConfig(BaseModel):
    api: XenAPIConfig
    endpoints: List[str]


class AWSCredentialsConfig(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str


class AWSAccountConfig(BaseModel):
    credentials: AWSCredentialsConfig
    role_arn: str
    region: str
    endpoints: List[str]


class SaltConfig(BaseModel):
    api_url: str
    username: str
    password: str
    target_version: str


class NetBoxConfig(BaseModel):
    base_url: HttpUrl
    api_token: str


class PathsConfig(BaseModel):
    data_dir: Path
    reports_dir: Path


class OutputConfig(BaseModel):
    csv_path: Path


class Settings(BaseModel):
    xen: Dict[str, XenDatacenterConfig]
    aws: Dict[str, AWSAccountConfig]
    salt: SaltConfig
    netbox: NetBoxConfig
    paths: PathsConfig
    output: OutputConfig

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        """Loads, parses, and validates settings from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)


CONFIG_FILE_PATH = Path(__file__).parent / "config.yaml"
settings = Settings.from_yaml(CONFIG_FILE_PATH)
