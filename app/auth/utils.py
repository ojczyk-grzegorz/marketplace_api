import datetime as dt

import bcrypt
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def get_password_hash(password):
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    )


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


def validate_access_token(token: str, secret_key: str, algorithms: list[str]) -> int:
    payload: dict = jwt.decode(
        jwt=token, key=secret_key, algorithms=algorithms, options={"verify_exp": True}
    )

    return payload.get("user_id")
