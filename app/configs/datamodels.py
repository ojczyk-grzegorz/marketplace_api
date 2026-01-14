from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field("E-commerce API")
    environment: Environment = Field(Environment.DEVELOPMENT)
    logger_name: str = Field("ecommerce_api")
    logger_level: str = Field("INFO")

    db_host: str = Field("localhost")
    db_port: int = Field(5432)
    db_user: str
    db_password: str

    db_name: str = Field("ecommerce_api")

    auth_secret_key: str = Field(...)
    auth_algorithm: str = Field("HS256")
    auth_access_token_expire_minutes: int = Field(60 * 24)
