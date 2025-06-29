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
    results = db_search(f"SELECT row_to_json(users) FROM users WHERE uid = {user_id}")
    if results:
        return results[0][0]

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
    results = db_search(f"SELECT row_to_json(users) FROM users WHERE uid = {user_id}")
    if results:
        return results[0][0]

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
    results = db_search(f"SELECT row_to_json(users) FROM users WHERE email = '{user.email}'")
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
    # results = db_search(f"SELECT json_agg(transactions_active) FROM transactions_active WHERE buyer_id = {user_id}")
    sid_cancelled = db_search(f"SELECT sid FROM status WHERE name = 'cancelled'")
    sid_cancelled = sid_cancelled[0][0]

    trans_update = db_update(
        table="transactions_active",
        data={"status_id": sid_cancelled},
        where=f"buyer_id = {user_id} AND transaction_end IS NULL",
    )

    tranasctions = db_search(
        f"SELECT json_agg(transactions_active) FROM transactions_active WHERE buyer_id = {user_id}"
    )[0][0]

    

    return tranasctions


    return trans_update
    results = db_remove(table="users", where=f"uid = {user_id}")
    results = db_remove(table="users", where=f"uid = {user_id}")
    if results:
        return {"message": "User removed successfully", "uid": user_id}
    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user_id})
