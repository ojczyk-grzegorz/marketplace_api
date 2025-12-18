import datetime as dt

from typing import Annotated
from fastapi import APIRouter, Body, status, Depends, Request
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.utils.db import (
    get_db_session,
    db_search_simple,
    db_insert,
    db_remove,
)
from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.auth import get_password_hash
from app.datamodels.user import (
    UserDBOutDetailed,
    UserCreate,
    UserDBIn,
)
from app.datamodels.response import ResponseSuccess
from app.exceptions.exceptions import (
    ExcUserNotFound,
    ExcUserExists,
    ExcTransactionsFound,
)
from app.utils.auth import validate_access_token, oauth2_scheme


router = APIRouter(prefix="/users", tags=["Users"], route_class=APIRoute)


# CREATE USER
# UPDATE EMAIL/PHONE/PASSWORD
# REMOVE USER


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_create(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    user: UserCreate = Body(
        ...,
        openapi_examples={
            "example1": {
                "summary": "Example user creation payload",
                "value": {
                    "email": "user@example.com",
                    "phone": "+48123456789",
                    "password": "strongpassword123",
                },
            }
        },
    ),
):
    db_users_matching = db.execute(
        text(
            "SELECT email, phone FROM "
            + settings.db_table_users
            + " WHERE email = :email OR phone = :phone LIMIT 1"
        ),
        params={"email": user.email, "phone": user.phone},
    ).fetchone()
    if db_users_matching:
        raise ExcUserExists(
            email=user.email
            if db_users_matching._mapping["email"] == user.email
            else None,
            phone=user.phone
            if db_users_matching._mapping["phone"] == user.phone
            else None,
        )

    created_at = dt.datetime.now(dt.timezone.utc)

    user = UserDBIn(
        **user.model_dump(),
        password_hash=get_password_hash(user.password),
        created_at=created_at,
        updated_at=created_at,
    )

    db_user_new: dict = db.execute(
        text(
            "INSERT INTO "
            + settings.db_table_users
            + " (user_id, email, phone, password_hash, created_at, updated_at) "
            "VALUES (:user_id, :email, :phone, :password_hash, :created_at, :updated_at) "
            "RETURNING email, phone, created_at"
        ),
        params=user.model_dump(exclude_none=True, mode="json"),
    ).fetchone()
    db.commit()
    return ResponseSuccess(
        message="User created successfully",
        details=dict(user=dict(db_user_new._mapping)),
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
