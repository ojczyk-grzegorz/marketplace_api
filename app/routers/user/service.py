import datetime as dt

from sqlmodel import Session, delete, select, update

from app.auth.utils import get_password_hash, validate_access_token
from app.configs.datamodels import Settings
from app.database.dbmodels import DBTransaction, DBUser
from app.exceptions.exceptions import (
    ExcTransactionsActiveFound,
    ExcUserExists,
    ExcUserNotFound,
)
from app.routers.user.datamodels import (
    ResponseCreateUser,
    ResponseRemoveUser,
    ResponseUpdateUser,
    UserCreated,
    UserRemoved,
    UserToCreate,
    UserToUpdate,
    UserUpdated,
)


async def create_user(db: Session, user_req: UserToCreate) -> ResponseCreateUser:
    query = select(DBUser).where(
        (DBUser.email == user_req.email) | (DBUser.phone == user_req.phone)
    )
    user_db: DBUser | None = db.exec(query).first()
    if user_db:
        raise ExcUserExists(
            email=(user_req.email if user_db.email == user_req.email else None),
            phone=(user_req.phone if user_db.phone == user_req.phone else None),
        )

    try:
        created_at = dt.datetime.now(dt.timezone.utc)
        user_db = DBUser(
            email=user_req.email,
            phone=user_req.phone,
            password_hash=get_password_hash(user_req.password),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        raise e

    return ResponseCreateUser(
        user_created=UserCreated(
            user_id=user_db.user_id, email=user_req.email, phone=user_req.phone
        ),
    )


async def update_user(
    settings: Settings,
    db: Session,
    token: str,
    user: UserToUpdate,
) -> ResponseUpdateUser:
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
        user_db_update["password_hash"] = get_password_hash(user.password)
    try:
        query = update(DBUser).where(DBUser.user_id == user_id).values(user_db_update)
        db.exec(query)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        raise e

    return ResponseUpdateUser(
        user_updated=UserUpdated(
            user_id=user_id,
            email=user_db.email,
            phone=user_db.phone,
            password_changed=bool(user.password),
        ),
    )


async def remove_user(
    settings: Settings,
    db: Session,
    token: str,
) -> ResponseRemoveUser:
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
    phone = user_db.phone

    query = select(DBTransaction).where(DBTransaction.user_id == user_id)
    db_user_transactions = db.exec(query).all()
    if db_user_transactions:
        raise ExcTransactionsActiveFound(
            user_id=user_id,
            transaction_ids=[t.transaction_id for t in db_user_transactions],
        )

    try:
        query = delete(DBUser).where(DBUser.user_id == user_id)
        db.exec(query)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return ResponseRemoveUser(
        user_removed=UserRemoved(user_id=user_id, email=email, phone=phone),
    )
