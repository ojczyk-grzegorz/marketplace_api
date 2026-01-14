from fastapi.testclient import TestClient
import pytest
import pytest_mock

from app.auth.datamodels import ResponseGetToken
from app.configs.datamodels import Settings
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_req_get_token(mocker: pytest_mock.MockerFixture) -> None:
    mock_get_token = mocker.patch(
        "app.routers.auth.service.get_token",
        return_value=ResponseGetToken(
            access_token="testtoken",
            expires_in=3600,
            token_type="bearer",
        ),
    )
    await client.post("/v1/auth/token", data={"username": "username", "password": "password"})
    mock_get_token.assert_called_once_with(
        settings=Settings(),
        db=mocker.ANY,
        form=mocker.ANY,
    )
