from dataclasses import dataclass

from my_bot_name import config


@dataclass(frozen=True)
class ApiConfig:
    """
    API configuration class
    """

    host: str
    port: int
    reload: bool


@dataclass(frozen=True)
class GCPConfig:
    """
    GCP configuration class
    """

    project_id: str
    region: str
    temperature: float


API_CONFIG = ApiConfig(**config["api_config"])
GCP_CONFIG = GCPConfig(**config["gcp_config"])
