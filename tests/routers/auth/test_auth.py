from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest

from app.auth.datamodels import ResponseGetToken
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
@patch("app.routers.auth.auth.get_token", new_callable=AsyncMock)
async def test_req_get_token(mock_get_token: AsyncMock) -> None:
    mock_get_token.return_value = ResponseGetToken(
        access_token="testtoken",
        expires_in=3600,
        token_type="bearer",
    )
    result = client.post("/v1/auth/token", data={"username": "username", "password": "password"})
    assert result.status_code == 200
    assert result.json() == {
        "access_token": "testtoken",
        "expires_in": 3600,
        "token_type": "bearer",
    }
    mock_get_token.assert_awaited_once()
