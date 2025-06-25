from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from db.db import database
from datamodels.response import ErrorResponse
from datamodels.auth import Token
from auth.auth import get_access_token, KEY, ALGORITHM, verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=Token | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    users_db: list[dict] = database["users"]

    email: str = form.username
    password: str = form.password

    for user in users_db:
        if user.get("email") == email and verify_password(password, user["password_hash"]):
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

    return ErrorResponse(
        error="INVALID_CREDENTIALS",
    )
