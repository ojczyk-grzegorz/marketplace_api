import json
from functools import lru_cache

from pydantic_settings import BaseSettings


class SettingsDBTable(BaseSettings):
    name: str


class SettingsDBTables(BaseSettings):
    users: SettingsDBTable
    items: SettingsDBTable
    transactions: SettingsDBTable
    logs_request: SettingsDBTable
    logs_query: SettingsDBTable


class SettingsAuth(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class SettingsDB(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    database: str
    tables: SettingsDBTables


class Settings(BaseSettings):
    app_name: str
    database: SettingsDB
    auth: SettingsAuth


@lru_cache()
def get_settings() -> Settings:
    with open("secrets/configs.json", "r") as f:
        settings_data = json.load(f)
        settings = Settings.model_validate(settings_data)
    return settings
