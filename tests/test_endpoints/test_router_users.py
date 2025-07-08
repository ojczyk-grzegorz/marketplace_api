import pytest
from fastapi.testclient import TestClient

from app.routers.users import router
from app.exceptions.exceptions import ExcUserNotFound

from tests.utils import TEST_SETTINGS


client = TestClient(router)


@pytest.mark.parametrize(
    "db_user, exception, expected_status_code, expected_response",
    [
        ({"uid": 1}, None, 200, {"uid": 1}),
        (
            {"uid": 1},
            ExcUserNotFound(user_id=1),
            404,
            {
                "code": "USER_NOT_FOUND",
                "message": "User with ID 1 not found.",
                "details": {"user_id": 1},
            },
        ),
    ],
)
def test_read_main(mocker, db_user, exception, expected_status_code, expected_response):
    mocker.patch("app.routers.users.get_settings", return_value=TEST_SETTINGS)

    if not exception:
        mocker.patch("app.routers.users.db_search_user_by_id", return_value=db_user)
    else:
        mocker.patch("app.routers.users.db_search_user_by_id", side_effect=exception)

    response = client.get(f"/users/user/{db_user['uid']}")
    response_body = response.json()
    response_body.pop("request_id", None)

    assert response.status_code == expected_status_code
    assert response_body == expected_response

