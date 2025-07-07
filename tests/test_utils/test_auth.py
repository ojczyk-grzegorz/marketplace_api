import pytest
import time
import jwt


from app.utils.auth import (
    get_password_hash,
    verify_password,
    get_access_token,
    validate_access_token,
)


@pytest.mark.parametrize(
    "password, password_verify, expected",
    [
        ("test_password", "test_password", True),
        ("test_password", "wrong_password", False),
    ],
)
def test_password_hash(password, password_verify, expected):
    hashed_password = get_password_hash(password)
    assert verify_password(password_verify, hashed_password) is expected


@pytest.mark.parametrize(
    "expire_minutes, sleep_time_seconds, override, exception",
    [
        (1, 1, None, None),
        (1 / 60, 2, None, jwt.exceptions.ExpiredSignatureError),
        (1, 1, "eyJhbGc.eyJ1c2Vy.g3to2hM", jwt.exceptions.DecodeError),
    ],
)
def test_get_token(expire_minutes, sleep_time_seconds, override, exception):
    data = {"user_id": 1}
    secret = "test_secret"
    algorithm = "HS256"

    token = get_access_token(data, secret, algorithm, expire_minutes)
    if override:
        token = override

    time.sleep(sleep_time_seconds)
    if exception:
        with pytest.raises(exception):
            validate_access_token(token, secret, [algorithm])
    else:
        user_id = validate_access_token(token, secret, [algorithm])
        assert user_id == data["user_id"]
