from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str
    logger_name: str
    logger_level: str

    db_host: str
    db_port: int
    db_user: str
    db_password: str

    db_schema: str
    db_table_users: str
    db_table_items: str
    db_table_transactions: str
    db_table_logs_request: str
    db_table_logs_query: str

    auth_secret_key: str
    auth_algorithm: str
    auth_access_token_expire_minutes: int
