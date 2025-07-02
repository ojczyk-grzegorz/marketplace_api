import datetime as dt

from fastapi import APIRouter, Path, Body, status, Depends


from db.db import db_search_simple, db_insert, db_update, db_remove
from auth.auth import get_password_hash
from datamodels.user import (
    UserDBOut,
    UserDBOutDetailed,
    UserCreate,
    UserUpdate,
    UserDBIn,
)
from datamodels.response import ErrorResponse
from auth.auth import validate_access_token, KEY, ALGORITHM, oauth2_scheme
from testing.openapi.users import USER_PATCH, USER_CREATE


router = APIRouter(prefix="/users", tags=["Users"])


def get_user_db_in(user: UserCreate) -> dict:
    created_at = dt.datetime.now(dt.timezone.utc)
    user = UserDBIn(
        **user.model_dump(exclude_none=True),
        password_hash=get_password_hash(user.password),
        created_at=created_at,
        updated_at=created_at,
    ).model_dump(exclude_none=True, exclude_unset=True, mode="json")

    return user


def get_user_by_id(user_id: int, columns: list[str]) -> dict | None:
    users = db_search_simple("users", columns, f"uid = {user_id}")
    return users[0] if users else None


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOut | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user(user_id: int = Path(...)):
    columns = UserDBOut.model_fields.keys()
    user = get_user_by_id(user_id, columns)

    if user:
        return user
    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.post(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOutDetailed | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user_me(token: str = Depends(oauth2_scheme)):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    columns = UserDBOutDetailed.model_fields.keys()
    user = get_user_by_id(user_id, columns)

    if user:
        return user
    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOutDetailed | ErrorResponse,
    description="Route for creating user",
)
async def user_create(
    user: UserCreate = Body(..., openapi_examples=USER_CREATE),
):
    user_db = db_search_simple(
        "users",
        ["email", "phone"],
        f"email = '{user.email}' OR phone = '{user.phone}'",
        "LIMIT 1",
    )
    if user_db:
        details = dict(email=(user.email, user[0][0]), phone=(user.phone, user[0][1]))
        return ErrorResponse(
            error="USER_ALREADY_EXISTS",
            details={k: v[0] for k, v in details.items() if v[0] == v[1]},
        )

    created_at = dt.datetime.now(dt.timezone.utc)

    user = UserDBIn(
        **user.model_dump(exclude_none=True, exclude=["password"]),
        password_hash=get_password_hash(user.password),
        created_at=created_at,
        updated_at=created_at,
    ).model_dump(exclude_none=True, mode="json")

    user: dict = db_insert("users", user, UserDBOutDetailed.model_fields.keys())

    return user


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOutDetailed | ErrorResponse,
    description="Route for creating user",
)
async def user_update(
    token: str = Depends(oauth2_scheme),
    user: UserUpdate = Body(
        ...,
        openapi_examples=USER_PATCH,
    ),
):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    user_db = db_search_simple(
        "users",
        ["uid"],
        f"uid = {user_id}",
        "LIMIT 1",
    )
    if not user_db:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"uid": user_id},
        )

    user_db = db_search_simple(
        "users",
        ["email", "phone"],
        f"email = '{user.email}' OR phone = '{user.phone}'",
        "LIMIT 1",
    )
    if user_db:
        details = dict(email=(user.email, user[0][0]), phone=(user.phone, user[0][1]))
        return ErrorResponse(
            error="USER_ALREADY_EXISTS",
            details={k: v[0] for k, v in details.items() if v[0] == v[1]},
        )

    user = UserDBIn(
        **user.model_dump(exclude_none=True, exclude=["password"]),
        password_hash=get_password_hash(user.password) if user.password else None,
        updated_at=dt.datetime.now(dt.timezone.utc),
    ).model_dump(exclude_none=True, mode="json")

    user = db_update(
        table="users",
        data=user,
        where=f"uid = {user_id}",
        columns_out=UserDBOutDetailed.model_fields.keys(),
    )
    if user:
        return user
    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user.uid})


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    response_model=dict | ErrorResponse,
    description="Route for creating user",
)
async def user_remove(
    token: str = Depends(oauth2_scheme),
):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    users = db_search_simple(
        "users",
        ["uid_uuid4"],
        f"uid = {user_id}",
        "LIMIT 1",
    )
    if not users:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"uid": user_id},
        )
    user_id_uuid4 = users[0]["uid_uuid4"]
    transaction_ids = db_search_simple(
        "transactions",
        ["tid"],
        f"finilized IS NULL AND (buyer_uid_uuid4 = '{user_id_uuid4}' OR seller_uid_uuid4 = '{user_id_uuid4}')",
    )
    if transaction_ids:
        return ErrorResponse(
            error="Close active transactions before removing user",
            details=dict(transaction_ids=transaction_ids),
        )

    db_remove("items", f"seller_id = {user_id}", columns_out=["iid"])
    users = db_remove(table="users", where=f"uid = {user_id}", columns_out=["email"])

    return dict(
        message="User removed successfully",
        details={
            "email": users[0]["email"],
            "uid": user_id,
            "uid_uuid4": user_id_uuid4,
        },
    )
