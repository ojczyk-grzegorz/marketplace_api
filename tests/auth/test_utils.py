import bcrypt
import jwt
import pytest

from app.auth.utils import (
    get_access_token,
    get_password_hash,
    validate_access_token,
    verify_password,
)
from app.exceptions.exceptions import ExcExpiredToken, ExcInvalidToken

SECRET_KEY = "KEYYYYYYY"
ALGORITHM = "HS256"


@pytest.fixture(name="token_data")
def fixture_token_data() -> dict:
    return dict(
        user_id="user-1234",
    )


@pytest.mark.parametrize(
    ("plain_password", "hashed_password", "expected"),
    [
        ("testpassword", "$2b$12$zhay85gNYhg10nZMQ5dJjurFfXvUIwz06IRgcrS4kxmb3Xk7drjry", True),
        (
            "TOTALLY_DIFFERENT_PASSWORD",
            "$2b$12$zhay85gNYhg10nZMQ5dJjurFfXvUIwz06IRgcrS4kxmb3Xk7drjry",
            False,
        ),
    ],
)
def test_verify_password(plain_password: str, hashed_password: str, expected: bool) -> None:
    assert verify_password(plain_password, hashed_password) is expected


def test_get_password_hash() -> None:
    assert isinstance(get_password_hash("testpassword"), str)
    assert bcrypt.checkpw(
        "testpassword".encode("utf-8"), get_password_hash("testpassword").encode("utf-8")
    )


@pytest.mark.parametrize(
    ("expire_minutes", "key", "expected"),
    [
        (15.0, SECRET_KEY, True),
        (15.0, SECRET_KEY + "WRONG", jwt.InvalidSignatureError),
        (-15.0, SECRET_KEY, jwt.ExpiredSignatureError),
    ],
)
def test_get_access_token(
    token_data: dict, expire_minutes: float, key: str, expected: bool | Exception
) -> None:
    token = get_access_token(
        data=token_data, secret_key=SECRET_KEY, algorithm=ALGORITHM, expire_minutes=expire_minutes
    )
    if isinstance(expected, bool):
        data = jwt.decode(
            jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True}
        )
        assert data["user_id"] == token_data["user_id"]
    else:
        with pytest.raises(expected):
            jwt.decode(jwt=token, key=key, algorithms=[ALGORITHM], options={"verify_exp": True})


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        # Working token for user_id "user-1234" expiring in 2126
        (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlci0xMjM0IiwiZXhwIjo0OTIyMDMxMzQyLjkxNTUwM30.F6CG7EIYp6LbQXjXziJcrY0CePkPyYzspor_EQykCmw",
            "user-1234",
        ),
        (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlci0xMjM0IiwiZXhwIjoxNzY4NDMwNDQyLjkxNTU4M30.kCs6WANzIq_XGaN6KRiaeHXh83V7UcaEEG6pmbMKbLY",
            ExcExpiredToken,
        ),
        (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlci0xMjM0IiwiZXhwIjo0OTIyMDMxMzQyLjkxNTYxfQ.e5PBhpzvwOstVkc99CurtHdNfXpm4mtwuWzDSVjtKoU",
            ExcInvalidToken,
        ),
    ],
)
def test_validate_access_token(token: str, expected: str | Exception) -> None:
    if isinstance(expected, str):
        user_id = validate_access_token(token=token, secret_key=SECRET_KEY, algorithms=[ALGORITHM])
        assert user_id == expected
    else:
        with pytest.raises(expected):
            validate_access_token(token=token, secret_key=SECRET_KEY, algorithms=[ALGORITHM])
