from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth.datamodels import ResponseGetToken
from app.auth.utils import get_access_token, verify_password
from app.configs.datamodels import Settings
from app.configs.utils import get_settings
from app.database.dbmodels import DBUser
from app.database.utils import get_db_session
from app.exceptions.exceptions import ExcInvalidCredentials


async def get_token(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> ResponseGetToken:
    query = select(DBUser).where(DBUser.email == form.username)
    db_user_matching = db.exec(query).first()

    if db_user_matching:
        password_valid = verify_password(form.password, db_user_matching.password_hash)
    else:
        password_valid = False
        verify_password(form.password, "$2b$12$dummy.hash.to.prevent.timing.attack.here.xxx")
    if not password_valid:
        raise ExcInvalidCredentials()

    token = get_access_token(
        data={"user_id": str(db_user_matching.user_id)},
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
        expire_minutes=settings.auth_access_token_expire_minutes,
    )

    return ResponseGetToken(
        access_token=token,
        expires_in=settings.auth_access_token_expire_minutes * 60,
        token_type="bearer",
    )
