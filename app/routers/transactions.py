import datetime as dt

from fastapi import APIRouter, status, Body, Depends, Request
from app.utils.auth import oauth2_scheme, validate_access_token
from app.datamodels.response import ResponseSuccess
from app.exceptions.exceptions import (
    ExcUserNotFound,
    ExcItemNotFound,
    ExcTransactionActiveNotFound,
)
from app.utils.db import db_search_simple, db_insert, db_update, db_remove
from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings

from app.datamodels.transaction import (
    TransactionCreate,
    TransactionDBIn,
    TransactionDBOut,
    TransactionFinilize,
)
from app.datamodels.item import ItemDB
from app.datamodels.user import UserDBOutDetailed
from tests.openapi.transactions import TRANSACTION_CREATE, TRANSACTION_FINILIZE


router = APIRouter(
    prefix="/transactions", tags=["Transactions"], route_class=APIRouteLogging
)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
)
async def transaction_create(
    req: Request,
    token: str = Depends(oauth2_scheme),
    req_body: TransactionCreate = Body(..., openapi_examples=TRANSACTION_CREATE),
):
    settings: Settings = get_settings()
    buyer_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    buyers = db_search_simple(
        table=settings.db_table_users,
        columns=UserDBOutDetailed.model_fields.keys(),
        where=f"uid = {buyer_id}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get"],
        ),
    )
    if not buyers:
        raise ExcUserNotFound(user_id=buyer_id)
    buyer = buyers[0]

    db_items = db_remove(
        table=settings.db_table_items,
        where=f"seller_id = {buyer_id} AND iid != {req_body.item_id}",
        columns_out=ItemDB.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "remove"],
        ),
    )
    if not db_items:
        raise ExcItemNotFound(item_id=req_body.item_id, not_user_id=buyer_id)

    db_item = db_items[0]
    sellers = db_search_simple(
        table=settings.db_table_users,
        columns=UserDBOutDetailed.model_fields.keys(),
        where=f"uid = {db_item['seller_id']}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get"],
        ),
    )
    seller = sellers[0]

    transaction = TransactionDBIn(
        sold_at=dt.datetime.now(dt.timezone.utc),
        item=db_item,
        seller_uid_uuid4=seller["uid_uuid4"],
        buyer_uid_uuid4=buyer["uid_uuid4"],
        seller_snapshot=seller,
        buyer_snapshot=buyer,
        finilized=None,
    )

    db_transactions = db_insert(
        table=settings.db_table_transactions,
        data=transaction.model_dump(exclude_none=True, mode="json"),
        columns_out=TransactionDBOut.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["transactions", "create"],
        ),
    )
    return ResponseSuccess(
        message="Transaction created successfully.",
        details={
            "transaction": db_transactions[0],
            "item_id": db_item["iid"],
            "seller_id": seller["uid"],
            "buyer_id": buyer["uid"],
        },
    )


@router.post(
    "/finilize",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
    description="Route for deleting an item",
)
async def transaction_finilize(
    req: Request,
    token: str = Depends(oauth2_scheme),
    req_body: TransactionFinilize = Body(..., openapi_examples=TRANSACTION_FINILIZE),
):
    settings: Settings = get_settings()
    buyer_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    db_buyers = db_search_simple(
        table=settings.db_table_users,
        columns=UserDBOutDetailed.model_fields.keys(),
        where=f"uid = {buyer_id}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get"],
        ),
    )
    if not db_buyers:
        raise ExcUserNotFound(user_id=buyer_id)

    db_buyer = db_buyers[0]
    buyer_uid_uuid4 = db_buyer["uid_uuid4"]

    db_transactions = db_update(
        table=settings.db_table_transactions,
        data={"finilized": dt.datetime.now(dt.timezone.utc).isoformat()},
        where=f"tid = {req_body.transaction_id} AND buyer_uid_uuid4 = '{buyer_uid_uuid4}' AND finilized IS NULL",
        columns_out=TransactionDBOut.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["transactions", "finilize"],
        ),
    )
    if not db_transactions:
        raise ExcTransactionActiveNotFound(
            transaction_id=req_body.transaction_id, user_id_uuid4=buyer_uid_uuid4
        )

    return ResponseSuccess(
        message="Transaction finilized successfully.",
        details={
            "transaction_id": req_body.transaction_id,
            "item": db_transactions[0]["item"],
        },
    )
