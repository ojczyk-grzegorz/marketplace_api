import datetime as dt

from typing import Annotated
from fastapi import APIRouter, Body, status, Depends
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


router = APIRouter(prefix="/users", tags=["Users"], route_class=APIRoute)


# UPDATE EMAIL/PHONE/PASSWORD


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
    db_user_matching = db.execute(
        text(
            "SELECT email, phone FROM "
            + settings.db_table_users
            + " WHERE email = :email OR phone = :phone LIMIT 1"
        ),
        params={"email": user.email, "phone": user.phone},
    ).fetchone()
    if db_user_matching:
        raise ExcUserExists(
            email=user.email
            if db_user_matching._mapping["email"] == user.email
            else None,
            phone=user.phone
            if db_user_matching._mapping["phone"] == user.phone
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


@router.patch(
    "/update",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_update(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user: UserUpdate = Body(
        ...,
        openapi_examples={
            "example1": {
                "summary": "Example user creation payload",
                "value": {
                    "email": "user2@example.com",
                    "phone": "+48234567891",
                    "password": "strongpassword456",
                },
            }
        },
    ),
):
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    db_user_matching = db.execute(
        text(
            "SELECT * FROM "
            + settings.db_table_users
            + " WHERE user_id = :user_id LIMIT 1"
        ),
        params={"user_id": user_id},
    ).fetchone()
    if not db_user_matching:
        raise ExcUserNotFound(
            user_id=user_id,
        )
    user_db_in = UserDBIn.model_validate({
        **db_user_matching._mapping,
        **user.model_dump(exclude_none=True),
    })
    user_db_in.updated_at = dt.datetime.now(dt.timezone.utc)
    if user.password:
        user_db_in.password_hash = get_password_hash(user.password)

    db_user_updated: dict = db.execute(
        text(
            "UPDATE"
            + " " + settings.db_table_users
            + " SET"
            + " user_id = :user_id, email = :email, phone = :phone, password_hash = :password_hash, created_at = :created_at, updated_at = :updated_at"
            + " WHERE user_id = :user_id"
            + " RETURNING email, phone, updated_at"
        ),
        params={"user_id": user_id, **user_db_in.model_dump(exclude_none=True, mode="json")},
    ).fetchone()
    db.commit()
    return ResponseSuccess(
        message="User updated successfully",
        details=dict(user=dict(db_user_updated._mapping)),
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseSuccess,
    description="Route for creating user",
)
async def user_remove(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: str = Depends(oauth2_scheme),
):
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )

    db_user_matching = db.execute(
        text(
            "SELECT user_id FROM "
            + settings.db_table_users
            + " WHERE user_id = :user_id LIMIT 1"
        ),
        params={"user_id": user_id},
    ).fetchone()

    if not db_user_matching:
        raise ExcUserNotFound(user_id=user_id)

    db_user_tranasactions = db.execute(
        text(
            "SELECT transaction_id FROM "
            + settings.db_table_transactions
            + " WHERE user_id = :user_id"
        ),
        params={"user_id": user_id},
    ).fetchall()
    if db_user_tranasactions:
        raise ExcTransactionsFound(
            user_id=user_id,
            details=dict(
                transaction_ids=[
                    t._mapping["transaction_id"] for t in db_user_tranasactions
                ]
            ),
        )

    db_user_removed = db.execute(
        text(
            "DELETE FROM "
            + settings.db_table_users
            + " WHERE user_id = :user_id RETURNING email"
        ),
        params={"user_id": user_id},
    ).fetchone()
    db.commit()

    return ResponseSuccess(
        message="User removed successfully",
        details={
            "user_id": user_id,
            "email": db_user_removed._mapping["email"],
        },
    )
