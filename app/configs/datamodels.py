from typing import Annotated
from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: Annotated[str, Field("Generic E-commerce API")]
    environment: Annotated[Environment, Field(Environment.DEVELOPMENT)]
    logger_name: Annotated[str, Field("generic_ecommerce_api")]
    logger_level: Annotated[str, Field("INFO")]

    db_host: Annotated[str, Field("localhost")]
    db_port: Annotated[int, Field(5432)]
    db_user: Annotated[str, Field(...)]
    db_password: Annotated[str, Field(...)]
    db_name: Annotated[str, Field("generic_ecommerce_api")]

    auth_secret_key: Annotated[str, Field(...)]
    auth_algorithm: Annotated[str, Field("HS256")]
    auth_access_token_expire_minutes: Annotated[int, Field(60 * 24)]
