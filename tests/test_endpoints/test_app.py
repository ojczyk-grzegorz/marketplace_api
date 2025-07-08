from fastapi.testclient import TestClient

from app.app import app

from tests.utils import TEST_SETTINGS


client = TestClient(app)


def test_read_main(mocker):
    mocker.patch("app.app.get_settings", return_value=TEST_SETTINGS)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello from {TEST_SETTINGS.app_name}!"}
