from tests.test_utils.utils import CONFIGS_JSON
from app.utils.configs import get_settings, Settings


def test_get_settings(mocker):
    mocker.patch(
        "builtins.open"
    ).return_value.__enter__.return_value.read.return_value = CONFIGS_JSON
    settings = get_settings()
    assert settings == Settings.model_validate_json(CONFIGS_JSON)
