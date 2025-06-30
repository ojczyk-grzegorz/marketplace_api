import datetime as dt

from fastapi import APIRouter, Path, Body, status, Depends


from db.db import database, db_search, db_insert, db_update, db_remove
from datamodels.user import UserCreate, UserDB, UserPatch, UserOut, Address
from datamodels.response import ErrorResponse
from auth.auth import validate_access_token, KEY, ALGORITHM, oauth2_scheme
from testing.openapi.users import USER_CREATE, USER_PATCH


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user(
    user_id: int = Path(...)
):
    results = db_search(f"SELECT json_agg(users) FROM users WHERE uid = {user_id}")[0][0][0]
    if results:
        return results

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
    results = db_search(f"SELECT json_agg(users) FROM users WHERE uid = {user_id}")[0][0]
    if results:
        return results[0]

    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=UserDB | ErrorResponse,
    description="Route for creating user",
)
async def create_customers(
    user: UserCreate = Body(..., openapi_examples=USER_CREATE),
):
    results = db_search(f"SELECT json_agg(users) FROM users WHERE email = '{user.email}'")
    if results:
        return ErrorResponse(
            error="USER_ALREADY_EXISTS", details={"email": user.email}
        )

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
    )

    results = db_insert("users", user.model_dump(exclude_none=True, exclude_unset=True, mode="json"))
    return results[0][0]


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for creating user",
)
async def update_customers(
    token: str = Depends(oauth2_scheme),
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
    results = db_update(
        table="users",
        data=user.model_dump(exclude_none=True, exclude_unset=True),
        where=f"uid = {user_id}",
    )
    if results:
        return results[0][0] 
    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user.uid})


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    # response_model=dict | ErrorResponse,
    description="Route for creating user",
)
async def update_customers(
    token: str = Depends(oauth2_scheme),
):
    user_id = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    
    results = db_search(f"""
        SELECT json_agg(transactions_active)
        FROM transactions_active
        WHERE (
            buyer_id = {user_id}
            AND transaction_end IS NULL
        )
    """)[0][0]
    if results:
        return ErrorResponse(
            error="Close active transactions before removing user",
            details=dict(
                transactions=results
            )
        )
    

    tids = db_search(f"""
        SELECT tid
        FROM transactions_active
        WHERE (
            buyer_id = {user_id}
            AND transaction_end IS NOT NULL
        );
    """)
    if tids:
        results = db_search(
            f"""
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
                        buyer_id = 2
                        AND transaction_end IS NOT NULL
                    )
                )
                RETURNING row_to_json(transactions_archived);

            """
        )

        db_remove(
            table="items",
            where=f"transaction_id IN ({", ".join(str(x[0]) for x in tids)})"
        )

        print([", ".join(str(x) for x in tids)])

        db_remove(
            table="transactions_active",
            where=f"buyer_id = {user_id} AND transaction_end IS NOT NULL"
        )

    results = db_search(f"""
        SELECT json_agg(items)
        FROM items
        WHERE seller_id = {user_id}
    """)[0][0]
    
    if results:
        return ErrorResponse(
            error="Remove active items and close all transactions before removing user",
            details=dict(
                items=results
            )
        )
    
    
    
    
    results = db_remove(table="users", where=f"uid = {user_id}")[0][0]
    if results:
        return {"message": "User removed successfully", "uid": user_id}
    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user_id})
