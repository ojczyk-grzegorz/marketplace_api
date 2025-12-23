from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.datamodels.auth import BearerToken
from app.datamodels.configs import Settings
from app.dbmodels.dbmodels import DBUser
from app.exceptions.exceptions import ExcInvalidCredentials
from app.utils.auth import get_access_token, verify_password
from app.utils.configs import get_settings
from app.utils.db import get_db_session


async def get_token(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    query = select(DBUser).where(DBUser.email == form.username)
    db_user_matching = db.exec(query).first()

    if not db_user_matching or not verify_password(
        form.password, db_user_matching.password_hash
    ):
        raise ExcInvalidCredentials()

    token = get_access_token(
        data={"user_id": db_user_matching.user_id.hex},
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        expire_minutes=settings.auth_access_token_expire_minutes,
    )

    return BearerToken(
        access_token=token,
    )
