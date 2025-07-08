from tests.utils import TEST_CONFIGS_JSON, TEST_SETTINGS
from app.utils.configs import get_settings, Settings


def test_get_settings(mocker):
    mocker.patch(
        "builtins.open"
    ).return_value.__enter__.return_value.read.return_value = TEST_CONFIGS_JSON
    settings = get_settings()
    assert settings == TEST_SETTINGS
