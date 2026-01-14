import datetime as dt
import uuid

import bcrypt
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.exceptions.exceptions import ExcExpiredToken, ExcInvalidToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def get_access_token(data: dict, secret_key: str, algorithm: str, expire_minutes: int) -> str:
    token = jwt.encode(
        payload=dict(
            **data,
            exp=(
                dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=expire_minutes)
            ).timestamp(),
        ),
        key=secret_key,
        algorithm=algorithm,
    )
    return token


def validate_access_token(token: str, secret_key: str, algorithms: list[str]) -> uuid.UUID:
    try:
        payload: dict = jwt.decode(
            jwt=token, key=secret_key, algorithms=algorithms, options={"verify_exp": True}
        )
    except jwt.ExpiredSignatureError as e:
        raise ExcExpiredToken() from e
    except jwt.InvalidTokenError as e:
        raise ExcInvalidToken from e

    return payload.get("user_id")
