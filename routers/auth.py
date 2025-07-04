from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from db.db import db_search_simple
from datamodels.auth import Token
from auth.auth import get_access_token, KEY, ALGORITHM, verify_password
from exceptions.exceptions import ExcInvalidCredentials


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    description="Route for getting user by ID",
)
async def get_token(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    users = db_search_simple(
        "users",
        ["uid", "email", "password_hash"],
        f"email = '{form.username}'",
        "LIMIT 1",
    )
    user = users[0] if users else None
    if not user or not verify_password(form.password, user["password_hash"]):
        raise ExcInvalidCredentials()

    token = get_access_token(
        data={"user_id": user["uid"]},
        secret_key=KEY,
        algorithm=ALGORITHM,
        expire_minutes=60,
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )
