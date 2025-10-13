from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import yaml
from pydantic import BaseModel, HttpUrl


def format_datetime(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


ALLOWED_FUNCTIONS = {
    "format_datetime": format_datetime,
}


def lambda_constructor(loader, node):
    value = loader.construct_scalar(node)
    return eval(f"lambda {value}")


def function_constructor(loader, node):
    value = loader.construct_scalar(node)
    if value in ALLOWED_FUNCTIONS:
        return ALLOWED_FUNCTIONS[value]
    raise yaml.constructor.ConstructorError(
        f"Function '{value}' is not in ALLOWED_FUNCTIONS."
    )


def get_yaml_loader():
    loader = yaml.SafeLoader
    loader.add_constructor("!lambda", lambda_constructor)
    loader.add_constructor("!function", function_constructor)
    return loader


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
    ssl: bool


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
    device_export_map: Dict[str, Tuple[str, Optional[Callable]]]
    vm_export_map: Dict[str, Tuple[str, Optional[Callable]]]

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        """Loads, parses, and validates settings from a YAML file."""
        with open(path, "r") as f:
            data = yaml.load(f, Loader=get_yaml_loader())
        return cls(**data)


CONFIG_FILE_PATH = Path(__file__).parent / "config.yaml"
settings = Settings.from_yaml(CONFIG_FILE_PATH)
