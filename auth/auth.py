import jwt
import datetime as dt

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


KEY = "SECRET"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    # return pwd_context.hash(password)
    return password + "_hash"


def verify_password(plain_password, hashed_password):
    # return pwd_context.verify(plain_password, hashed_password)
    return get_password_hash(plain_password) == hashed_password


def get_access_token(
    data: dict, secret_key: str, algorithm: str, expire_minutes: int
) -> str:
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
