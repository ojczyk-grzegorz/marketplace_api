import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.routing import APIRoute
from sqlmodel import Session, delete, insert, select, update

from app.datamodels.response import (
    DetailsUserCreate,
    DetailsUserRemove,
    DetailsUserUpdate,
    ResponseUserCreate,
    ResponseUserRemove,
    ResponseUserUpdate,
)
from app.datamodels.user import (
    UserCreate,
    UserUpdate,
)
from app.dbmodels.dbmodels import DBTransaction, DBUser
from app.exceptions.exceptions import (
    ExcTransactionsActiveFound,
    ExcUserExists,
    ExcUserNotFound,
)
from app.utils.auth import get_password_hash, oauth2_scheme, validate_access_token
from app.utils.configs import Settings, get_settings
from app.utils.db import (
    get_db_session,
)
from development.openapi_examples import (
    get_user_create_examples,
    get_user_update_examples,
)

router = APIRouter(prefix="/users", tags=["Users"], route_class=APIRoute)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseUserCreate,
    response_model_exclude_none=True,
    description="Route for creating user",
)
async def user_create(
    db: Annotated[Session, Depends(get_db_session)],
    user_req: Annotated[
        UserCreate,
        Body(..., openapi_examples=get_user_create_examples()),
    ],
):
    query = select(DBUser).where(
        (DBUser.email == user_req.email) | (DBUser.phone == user_req.phone)
    )
    user_db: DBUser | None = db.exec(query).first()
    if user_db:
        raise ExcUserExists(
            email=(user_req.email if user_db.email == user_req.email else None),
            phone=(user_req.phone if user_db.phone == user_req.phone else None),
        )

    created_at = dt.datetime.now(dt.timezone.utc)
    user_db = DBUser(
        email=user_req.email,
        phone=user_req.phone,
        password_hash=get_password_hash(user_req.password).decode("utf-8"),
        created_at=created_at,
        updated_at=created_at,
    )
    query = insert(DBUser).values(
        {**user_db.model_dump(), "password_hash": user_db.password_hash}
    )
    db.exec(query)
    db.commit()

    return ResponseUserCreate(
        details=DetailsUserCreate(email=user_req.email, phone=user_req.phone),
    )


@router.patch(
    "/update",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseUserUpdate,
    response_model_exclude_none=True,
    description="Route for updating user",
)
async def user_update(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user: Annotated[
        UserUpdate,
        Body(..., openapi_examples=get_user_update_examples()),
    ],
):
    user_id = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBUser).where(DBUser.user_id == user_id)
    user_db = db.exec(query).first()
    if not user_db:
        raise ExcUserNotFound(
            user_id=user_id,
        )

    user_db_update = dict(
        updated_at=dt.datetime.now(dt.timezone.utc),
        **user.model_dump(exclude_none=True),
    )
    if user.password:
        user_db_update["password_hash"] = get_password_hash(user.password).decode(
            "utf-8"
        )

    db_user = DBUser.model_validate(user_db)

    query = update(DBUser).where(DBUser.user_id == user_id).values(user_db_update)
    db.exec(query)
    db.commit()

    return ResponseUserUpdate(
        details=DetailsUserUpdate(
            email=db_user.email,
            phone=db_user.phone,
            password_changed=bool(user.password),
        ),
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseUserRemove,
    response_model_exclude_none=True,
    description="Route for removing user",
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

    query = select(DBUser).where(DBUser.user_id == user_id)
    user_db = db.exec(query).first()
    if not user_db:
        raise ExcUserNotFound(user_id=user_id)

    email = user_db.email

    query = select(DBTransaction).where(DBTransaction.user_id == user_id)
    db_user_tranasactions = db.exec(query).all()
    if db_user_tranasactions:
        raise ExcTransactionsActiveFound(
            user_id=user_id,
            transaction_ids=[t.transaction_id for t in db_user_tranasactions],
        )

    query = delete(DBUser).where(DBUser.user_id == user_id)
    db.exec(query)
    db.commit()

    return ResponseUserRemove(
        details=DetailsUserRemove(email=email, phone=user_db.phone),
    )
