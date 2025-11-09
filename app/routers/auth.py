from typing import Annotated

from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.db import db_search_simple
from app.utils.auth import get_access_token, verify_password
from app.datamodels.auth import Token
from app.exceptions.exceptions import ExcInvalidCredentials


router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=APIRouteLogging)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    description="Route for getting user by ID",
)
async def get_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    req: Request,
):
    settings: Settings = get_settings()
    users = db_search_simple(
        settings.db_table_users,
        ["uid", "email", "password_hash"],
        f"email = '{form.username}'",
        "LIMIT 1",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["token", "get"],
        ),
    )
    user = users[0] if users else None
    if not user or not verify_password(form.password, user["password_hash"]):
        raise ExcInvalidCredentials()

    token = get_access_token(
        data={"user_id": user["uid"]},
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        expire_minutes=settings.auth_access_token_expire_minutes,
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )
