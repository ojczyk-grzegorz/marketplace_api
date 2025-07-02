import datetime as dt

from fastapi import APIRouter, status, Body, Depends
from auth.auth import oauth2_scheme, validate_access_token, KEY, ALGORITHM

from db.db import db_search_simple, db_insert, db_update, db_remove
from datamodels.response import ErrorResponse
from datamodels.transaction import (
    TransactionCreate,
    TransactionDBIn,
    TransactionDBOut,
    TransactionFinilize,
)
from datamodels.item import ItemDB
from datamodels.user import UserDBOutDetailed
from testing.openapi.transactions import TRANSACTION_CREATE


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=TransactionDBOut | ErrorResponse,
)
async def transaction_create(
    token: str = Depends(oauth2_scheme),
    req_body: TransactionCreate = Body(..., openapi_examples=TRANSACTION_CREATE),
):
    buyer_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    buyers = db_search_simple(
        "users",
        UserDBOutDetailed.model_fields.keys(),
        f"uid = {buyer_id}",
    )
    if not buyers:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": buyer_id},
        )
    buyer = buyers[0]

    items = db_remove(
        "items",
        f"seller_id = {buyer_id} AND iid != {req_body.item_id}",
        columns_out=ItemDB.model_fields.keys(),
    )
    if not items:
        return ErrorResponse(
            error="ITEMS_NOT_FOUND",
            details={"item_ids": req_body.item_id, "buyer_id": buyer_id},
        )
    item = items[0]
    sellers = db_search_simple(
        "users",
        UserDBOutDetailed.model_fields.keys(),
        f"uid = {item['seller_id']}",
    )
    seller = sellers[0]

    transaction = TransactionDBIn(
        sold_at=dt.datetime.now(dt.timezone.utc),
        item=item,
        seller_uid_uuid4=seller["uid_uuid4"],
        buyer_uid_uuid4=buyer["uid_uuid4"],
        seller_snapshot=seller,
        buyer_snapshot=buyer,
        finilized=False,
    )

    transactions = db_insert(
        "transactions",
        transaction.model_dump(exclude_none=True, mode="json"),
        TransactionDBOut.model_fields.keys(),
    )

    return transactions[0]


@router.post(
    "/finilize",
    status_code=status.HTTP_200_OK,
    response_model=TransactionDBOut | ErrorResponse,
    description="Route for deleting an item",
)
async def transaction_finilize(
    token: str = Depends(oauth2_scheme),
    req_body: TransactionFinilize = Body(..., openapi_examples=TRANSACTION_CREATE),
):
    buyer_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    buyers = db_search_simple(
        "users",
        UserDBOutDetailed.model_fields.keys(),
        f"uid = {buyer_id}",
    )
    if not buyers:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": buyer_id},
        )
    buyer = buyers[0]
    buyer_uid_uuid4 = buyer["uid_uuid4"]

    transactions = db_update(
        "transactions",
        {"finilized": True},
        f"tid = {req_body.transaction_id} AND buyer_uid_uuid4 = '{buyer_uid_uuid4}' AND finilized = FALSE",
        TransactionDBOut.model_fields.keys(),
    )
    if not transactions:
        return ErrorResponse(
            error="TRANSACTION_NOT_FOUND",
            details={
                "transaction_id": req_body.transaction_id,
                "buyer_uid_uuid4": buyer_uid_uuid4,
            },
        )
    transaction = transactions[0]
    return transaction
