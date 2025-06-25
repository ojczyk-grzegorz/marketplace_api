import jwt
import datetime as dt

KEY = "SECRET"
ALGORITHM = "HS256"


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


def validate_access_token(
    token: str, secret_key: str, algorithms: list[str], user_id: int
) -> dict | None:
    payload: dict = jwt.decode(
        jwt=token, key=secret_key, algorithms=algorithms, options={"verify_exp": True}
    )

    if payload.get("user_id") != user_id:
        raise ValueError("Invalid user ID in token")

    return True
