import datetime as dt
from typing import Annotated
import copy

from fastapi import APIRouter, Path, Body, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from db.db import database
from datamodels.user import UserCreate, UserDB, UserPatch, UserOut, Address
from datamodels.response import ErrorResponse
from datamodels.auth import Token
from auth.auth import get_access_token, validate_access_token, KEY, ALGORITHM, verify_password, oauth2_scheme
from testing.openapi.users import USER_CREATE, USER_PATCH


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user(
    user_id: int = Path(
        ...,
    ),
):
    for user in database["users"]:
        if user.get("uid") == user_id:
            reviews = user.get("reviews", [])
            if len(reviews) > 3:
                user = copy.deepcopy(user)
                user["reviews"] = reviews[len(reviews) - 3 :]
            return user

    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserDB | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user_me(token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    for user in database["users"]:
        if user.get("uid") == user_id:
            reviews = user.get("reviews", [])
            if len(reviews) > 3:
                user["reviews"] = reviews[len(reviews) - 3 :]
            break

    else:
        return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})

    return user


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for creating user",
)
async def create_customers(
    user: UserCreate = Body(..., openapi_examples=USER_CREATE),
):
    db_users: list[dict] = database["users"]
    for du in db_users:
        if du.get("email") == user.email:
            return ErrorResponse(
                error="USER_ALREADY_EXISTS", details={"email": user.email}
            )

    user_id = max([x["uid"] for x in db_users], default=0) + 1
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()

    user = UserDB(
        **user.model_dump(exclude_none=True, exclude_unset=True),
        uid=user_id,
        created_at=created_at,
        updated_at=created_at,
        addresses=[
            Address(
                type="home",
                **user.model_dump(exclude_none=True, exclude_unset=True),
            )
        ],
        reviews=[],
        rating=0.0,
        avatar=None,
        last_activity=created_at,
    )

    db_users.append(user.model_dump())

    return user


@router.patch(
    "/me/update",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for creating user",
)
async def update_customers(
    token: Annotated[str, Depends(oauth2_scheme)],
    user: UserPatch = Body(
        ...,
        openapi_examples=USER_PATCH,
    ),
):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    db_users: list[dict] = database["users"]
    for du in db_users:
        if du.get("uid") == user_id:
            du.update(user.model_dump(exclude_none=True, exclude_unset=True))
            reviews = du.get("reviews", [])
            if len(reviews) > 3:
                du["reviews"] = reviews[len(reviews) - 3 :]
            return du

    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user.uid})
