from functools import lru_cache

from app.configs.datamodels import Settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()
