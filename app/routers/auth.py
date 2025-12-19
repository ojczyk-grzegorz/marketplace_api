from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.db import get_db_session, db_search_simple
from app.utils.auth import get_access_token, verify_password
from app.datamodels.auth import Token
from app.exceptions.exceptions import ExcInvalidCredentials


router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=APIRoute)


# TOKEN GENERATION


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    description="Route for getting user by ID",
)
async def get_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
):
    db_user_matching = db.execute(
        text(
            "SELECT user_id, password_hash FROM "
            + settings.db_table_users
            + " WHERE email = :email"
        ),
        params={"email": form.username},
    ).fetchone()

    if not db_user_matching or not verify_password(
        form.password, db_user_matching._mapping["password_hash"]
    ):
        raise ExcInvalidCredentials()

    token = get_access_token(
        data={"user_id": db_user_matching._mapping["user_id"].hex},
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        expire_minutes=settings.auth_access_token_expire_minutes,
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )
