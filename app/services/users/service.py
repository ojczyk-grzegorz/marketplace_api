import datetime as dt

from sqlmodel import Session, delete, insert, select, update

from app.datamodels.configs import Settings
from app.datamodels.user import (
    ResponseCreateUser,
    ResponseRemoveUser,
    ResponseUpdateUser,
    UserCreated,
    UserRemoved,
    UserToCreate,
    UserToUpdate,
    UserUpdated,
)
from app.dbmodels.dbmodels import DBTransaction, DBUser
from app.exceptions.exceptions import (
    ExcTransactionsActiveFound,
    ExcUserExists,
    ExcUserNotFound,
)
from app.utils.auth import get_password_hash, validate_access_token


async def create_user(db: Session, user_req: UserToCreate):
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

    return ResponseCreateUser(
        user_created=UserCreated(email=user_req.email, phone=user_req.phone),
    )


async def update_user(
    settings: Settings,
    db: Session,
    token: str,
    user: UserToUpdate,
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

    return ResponseUpdateUser(
        user_updated=UserUpdated(
            email=db_user.email,
            phone=db_user.phone,
            password_changed=bool(user.password),
        ),
    )


async def remove_user(
    settings: Settings,
    db: Session,
    token: str,
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

    return ResponseRemoveUser(
        user_removed=UserRemoved(email=email, phone=user_db.phone),
    )
