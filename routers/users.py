import datetime as dt

from fastapi import APIRouter, Path, Body, status, Depends


from db.db import db_query, db_search_simple, db_insert, db_update, db_remove
from datamodels.user import UserCreate, UserDB, UserPatch, UserOut, Address
from datamodels.response import ErrorResponse
from auth.auth import validate_access_token, KEY, ALGORITHM, oauth2_scheme
from testing.openapi.users import USER_CREATE, USER_PATCH


router = APIRouter(prefix="/users", tags=["Users"])


def get_user_by_id(user_id: int, columns: list[str]) -> dict | None:
    users = db_search_simple("users", columns, f"uid = {user_id}")
    return users[0] if users else None


def get_user_insert_data(user: UserCreate) -> dict:
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()

    user = UserDB(
        **user.model_dump(exclude_none=True),
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
    ).model_dump(exclude_none=True, exclude_unset=True, mode="json")

    return user


def move_closed_transactions_to_archive(user_id: int):
    transactions_closed_ids = db_search_simple(
        "transactions_active",
        ["tid"],
        f"buyer_id = {user_id} AND transaction_end IS NOT NULL",
    )
    if not transactions_closed_ids:
        return

    db_query(f"""
        INSERT INTO transactions_archived
        (
            SELECT
                tac.tid_uuid4,
                st.name AS status,
                tac.transaction_start,
                tac.transaction_end,
                it.iid_uuid4 AS item_id_uuid4,
                row_to_json(it) AS item_snapshot,
                usb.uid_uuid4 AS buyer_id_uuid4,
                row_to_json(usb) AS buyer_snapshot,
                uss.uid_uuid4 AS seller_id_uuid4,
                row_to_json(uss) AS seller_snapshot
            FROM transactions_active AS tac
            JOIN items AS it ON it.transaction_id = tac.tid
            JOIN status AS st ON st.sid = tac.status_id
            JOIN users AS usb ON usb.uid = tac.buyer_id
            JOIN users AS uss ON uss.uid = it.seller_id
            WHERE (
                buyer_id = {user_id}
                AND transaction_end IS NOT NULL
            )
        )
        RETURNING tid_uuid4
    """)

    db_remove(
        table="items",
        where=f"transaction_id IN ({', '.join(str(x['tid']) for x in transactions_closed_ids)})",
        columns_out=["iid"],
    )

    db_remove(
        table="transactions_active",
        where=f"buyer_id = {user_id} AND transaction_end IS NOT NULL",
        columns_out=["tid"],
    )


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user(user_id: int = Path(...)):
    columns = UserOut.model_fields.keys()
    user = get_user_by_id(user_id, columns)

    if user:
        return user
    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.post(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserDB | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user_me(token: str = Depends(oauth2_scheme)):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    columns = UserDB.model_fields.keys()
    user = get_user_by_id(user_id, columns)

    if user:
        return user
    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


