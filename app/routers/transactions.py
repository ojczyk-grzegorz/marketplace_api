from decimal import ROUND_CEILING, Decimal
from typing import Annotated
import uuid

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.routing import APIRoute
from sqlmodel import Session, select

from app.datamodels.response import ResponseTransaction, ResponseTransactionDetails, ResponseTransactionItem
from app.datamodels.transaction import (
    TransactionCreate,
)
from app.dbmodels.dbmodels import (
    DBDeliveryOptions,
    DBItem,
    DBTransaction,
    DBTransactionAction,
    DBTransactionDiscount,
    DBTransactionItem,
)
from app.utils.auth import oauth2_scheme, validate_access_token
from app.utils.configs import Settings, get_settings
from app.utils.db import (
    get_db_session,
)
from app.utils.transactions import (
    apply_discounts,
    check_for_item_snapshot,
    get_delivery_option_db,
    get_discount_db,
    get_item_db,
    update_item_stock,
)
from development.openapi_examples import get_transaction_create_examples

router = APIRouter(prefix="/transactions", tags=["Transactions"], route_class=APIRoute)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ResponseTransaction,
    response_model_exclude_none=True,
    description="Route for creating new transaction",
)
async def transaction_create(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    req_body: Annotated[
        TransactionCreate,
        Body(..., openapi_examples=get_transaction_create_examples()),
    ],
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    discounts_db = get_discount_db(db, req_body.discount_codes)
    delivery_option_db = get_delivery_option_db(db, req_body.delivery_option_id)

    transaction_id = uuid.uuid4()

    transaction_items_db = []
    response_transaction_items = []
    total_price = delivery_option_db.price
    for item_id, item_count in req_body.item_ids.items():
        item_db = get_item_db(db, item_id, item_count)
        update_item_stock(
            db,
            item_id,
            item_count,
        )
        check_for_item_snapshot(db, item_db)

        item_price = item_db.price
        price_after_discounts, applied_discounts = apply_discounts(
            item_db, item_price, discounts_db
        )

        response_transaction_item = ResponseTransactionItem(
            item_id=item_db.item_id,
            name=item_db.name,
            price_unit=item_price,
            price_after_discounts=price_after_discounts,
            count=item_count,
            applied_discounts=applied_discounts,
        )
        response_transaction_items.append(response_transaction_item)

        db_transaction_item = DBTransactionItem(
            transaction_id=transaction_id,
            item_id=item_db.item_id,
            item_updated_at=item_db.updated_at,
            count=item_count,
            price_after_discounts=price_after_discounts,
        )
        transaction_items_db.append(db_transaction_item)

        total_price += price_after_discounts * item_count

    total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    transaction_db = DBTransaction(
        transaction_id=transaction_id,
        user_id=user_id,
        delivery_option_id=req_body.delivery_option_id,
        transaction_details={
            "address": "Wawel Cathedral, Wawel, 31-001 Kraków, Poland",
        },
        total_price=total_price,
    )
    response_transaction_details = ResponseTransactionDetails(
            transaction_id=transaction_db.transaction_id,
            user_id=transaction_db.user_id,
            created_at=transaction_db.created_at,
            delivery_option=delivery_option_db.name,
            delivery_price=delivery_option_db.price,
            delivery_details=transaction_db.transaction_details,
            total_price=transaction_db.total_price,
        )
    db.add(transaction_db)

    transaction_discounts_db = [
        DBTransactionDiscount(
            transaction_id=transaction_id,
            discount_code=discount.discount_code,
        )
        for discount in discounts_db
    ]
    db.add_all(transaction_discounts_db)
    db.add_all(transaction_items_db)
    db.commit()

    return ResponseTransaction(
        transaction=response_transaction_details,
        items=response_transaction_items
    )


@router.get(
    "/current",
    status_code=status.HTTP_200_OK,
    response_model=ResponseTransactionDetails,
)
async def transactions_get_current(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: str = Depends(oauth2_scheme),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBTransaction).where(DBTransaction.user_id == user_id)
    transactions_db = db.exec(query).all()
    delivery_options = dict()
    transactions_response = []
    for transaction in transactions_db:
        delivery_option = delivery_options.get(transaction.delivery_option_id)
        if not delivery_option:
            query = select(DBDeliveryOptions).where(
                DBDeliveryOptions.option_id == transaction.delivery_option_id
            )
        delivery_option_db = db.exec(query).first()
        query = select(DBTransactionItem).where(
            DBTransactionItem.transaction_id == transaction.transaction_id
        )
        transaction_items_db = db.exec(query).all()
        transaction_items = []
        for item in transaction_items_db:
            query = select(DBItem).where(DBItem.item_id == item.item_id)
            item_db = db.exec(query).first()
            transaction_items.append(
                dict(
                    item_id=item.item_id,
                    name=item_db.name,
                    item_updated_at=item.item_updated_at,
                    count=item.count,
                    price_unit=item_db.price,
                    price_after_discounts=item.price_after_discounts,
                )
            )

        transaction_response = dict(
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            created_at=transaction.created_at,
            delivery_option=delivery_option_db.name,
            delivery_price=delivery_option_db.price,
            delivery_details=transaction.transaction_details,
            total_price=transaction.total_price,
            items=transaction_items,
        )
        transactions_response.append(transaction_response)

    return transactions_response


@router.get(
    "/status/{transaction_id}",
    status_code=status.HTTP_200_OK,
    # response_model=ResponseSuccess,
)
async def transaction_get_status(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    transaction_id: Annotated[
        uuid.UUID, Path(..., description="The UUID of the transaction to retrieve")
    ],
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBTransaction).where(
        (DBTransaction.user_id == user_id)
        & (DBTransaction.transaction_id == transaction_id)
    )
    transaction_db = db.exec(query).first()
    if not transaction_db:
        raise Exception("Transaction not found")

    query = (
        select(DBTransactionAction)
        .where(DBTransactionAction.transaction_id == transaction_id)
        .order_by(DBTransactionAction.performed_at.desc())
        .limit(1)
    )
    transaction_action_db = db.exec(query).first()
    return dict(
        transaction_id=transaction_db.transaction_id,
        status=transaction_action_db.action if transaction_action_db else None,
        status_time=transaction_action_db.performed_at
        if transaction_action_db
        else None,
    )
