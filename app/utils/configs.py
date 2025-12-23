from functools import lru_cache

from app.datamodels.configs import Settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()
