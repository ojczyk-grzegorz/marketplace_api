from unittest.mock import Mock, patch

import pytest

from app.auth.datamodels import ResponseGetToken
from app.configs.datamodels import Settings
from app.routers.auth.auth import get_token


@pytest.mark.asyncio
@patch("app.routers.auth.service.get_access_token")
@patch("app.routers.auth.service.select")
async def test_get_token(mock_select: Mock, mock_get_access_token: Mock) -> None:
    mock_db_session = Mock()
    mock_db_session.exec.return_value.first.return_value = Mock(
        user_id=1,
        email="testuser",
        password_hash="$2b$12$zhay85gNYhg10nZMQ5dJjurFfXvUIwz06IRgcrS4kxmb3Xk7drjry",
    )
    mock_get_access_token.return_value = "testtoken"
    result = await get_token(
        settings=Settings(),
        db=mock_db_session,
        form=Mock(username="testuser", password="testpassword"),
    )
    assert result == ResponseGetToken(
        access_token="testtoken",
        expires_in=Settings().auth_access_token_expire_minutes * 60,
        token_type="bearer",
    )
    mock_select.assert_called_once()
    mock_select.return_value.where.assert_called_once()
    mock_db_session.exec.assert_called_once_with(mock_select.return_value.where.return_value)
    mock_get_access_token.assert_called_once_with(
        data={"user_id": "1"},
        secret_key=Settings().auth_secret_key,
        algorithm=Settings().auth_algorithm,
        expire_minutes=Settings().auth_access_token_expire_minutes,
    )
