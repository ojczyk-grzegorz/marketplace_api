from app.configs.datamodels import Environment, Settings
from app.configs.utils import get_settings


def test_get_settings() -> None:
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.environment in Environment.TEST
