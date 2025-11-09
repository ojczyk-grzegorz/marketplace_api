import datetime as dt

from fastapi import APIRouter, Path, Body, status, Depends, Request

from app.utils.db import (
    db_search_simple,
    db_insert,
    db_update,
    db_remove,
    db_search_user_by_id,
)
from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.auth import get_password_hash
from app.datamodels.user import (
    UserDBOut,
    UserDBOutDetailed,
    UserCreate,
    UserUpdate,
    UserDBIn,
)
from app.datamodels.response import ResponseSuccess
from app.exceptions.exceptions import (
    ExcUserNotFound,
    ExcUserExists,
    ExcTransactionsFound,
)
from app.utils.auth import validate_access_token, oauth2_scheme
from tests.openapi.users import USER_PATCH, USER_CREATE


router = APIRouter(prefix="/users", tags=["Users"], route_class=APIRouteLogging)


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOut,
    description="Route for getting user by ID",
)
async def get_user(
    req: Request,
    user_id: int = Path(...),
):
    settings: Settings = get_settings()
    db_user = db_search_user_by_id(
        table=settings.db_table_users,
        user_id=user_id,
        columns=UserDBOut.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get"],
        ),
    )

    if not db_user:
        raise ExcUserNotFound(user_id=user_id)

    return db_user


@router.post(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserDBOutDetailed,
    description="Route for getting user by ID",
)
async def get_user_me(
    req: Request,
    token: str = Depends(oauth2_scheme),
):
    settings: Settings = get_settings()
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )

    db_user = db_search_user_by_id(
        table=settings.db_table_users,
        user_id=user_id,
        columns=UserDBOutDetailed.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get_me"],
        ),
    )

    if not db_user:
        raise ExcUserNotFound(user_id=user_id)
    return db_user


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_create(
    req: Request,
    user: UserCreate = Body(..., openapi_examples=USER_CREATE),
):
    settings: Settings = get_settings()
    db_users = db_search_simple(
        settings.db_table_users,
        ["email", "phone"],
        f"email = '{user.email}' OR phone = '{user.phone}'",
        "LIMIT 1",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "create"],
        ),
    )
    if db_users:
        raise ExcUserExists(
            email=user.email if db_users[0]["email"] == user.email else None,
            phone=user.phone if db_users[0]["phone"] == user.phone else None,
        )

    created_at = dt.datetime.now(dt.timezone.utc)

    user = UserDBIn(
        **user.model_dump(exclude_none=True, exclude=["password"]),
        password_hash=get_password_hash(user.password),
        created_at=created_at,
        updated_at=created_at,
    ).model_dump(exclude_none=True, mode="json")

    db_users: dict = db_insert(
        settings.db_table_users,
        user,
        UserDBOutDetailed.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "create"],
        ),
    )
    return ResponseSuccess(
        message="User created successfully",
        details=dict(user=db_users[0]),
    )


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_update(
    req: Request,
    token: str = Depends(oauth2_scheme),
    user: UserUpdate = Body(
        ...,
        openapi_examples=USER_PATCH,
    ),
):
    settings: Settings = get_settings()
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    db_users = db_search_simple(
        settings.db_table_users,
        ["uid"],
        f"uid = {user_id}",
        "LIMIT 1",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "update"],
        ),
    )
    if not db_users:
        raise ExcUserNotFound(user_id=user_id)

    user = UserDBIn(
        **user.model_dump(exclude_none=True, exclude=["password"]),
        password_hash=get_password_hash(user.password) if user.password else None,
        updated_at=dt.datetime.now(dt.timezone.utc),
    ).model_dump(exclude_none=True, mode="json")

    db_users = db_update(
        table=settings.db_table_users,
        data=user,
        where=f"uid = {user_id}",
        columns_out=UserDBOutDetailed.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "update"],
        ),
    )
    return ResponseSuccess(
        message="User updated successfully",
        details=dict(user=db_users[0]),
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_remove(
    req: Request,
    token: str = Depends(oauth2_scheme),
):
    settings: Settings = get_settings()
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )

    db_users = db_search_simple(
        settings.db_table_users,
        ["uid_uuid4"],
        f"uid = {user_id}",
        "LIMIT 1",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "remove"],
        ),
    )
    if not db_users:
        raise ExcUserNotFound(user_id=user_id)

    uid_uuid4 = db_users[0]["uid_uuid4"]
    transaction_ids = db_search_simple(
        settings.db_table_transactions,
        ["tid"],
        f"finilized IS NULL AND (buyer_uid_uuid4 = '{uid_uuid4}' OR seller_uid_uuid4 = '{uid_uuid4}')",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "remove"],
        ),
    )
    if transaction_ids:
        raise ExcTransactionsFound(
            user_id=user_id,
            details=dict(transaction_ids=[t["tid"] for t in transaction_ids]),
        )

    db_remove(
        settings.db_table_items,
        f"seller_id = {user_id}",
        columns_out=["iid"],
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "remove"],
        ),
    )
    db_users = db_remove(
        table=settings.db_table_users,
        where=f"uid = {user_id}",
        columns_out=["email"],
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "remove"],
        ),
    )

    return ResponseSuccess(
        message="User removed successfully",
        details={
            "email": db_users[0]["email"],
            "uid": user_id,
            "uid_uuid4": uid_uuid4,
        },
    )
