from decimal import ROUND_CEILING, Decimal
from typing import Annotated
import uuid

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.routing import APIRoute
from sqlmodel import Session, insert, select, update

from app.datamodels.transaction import (
    TransactionCreate,
)
from app.dbmodels.dbmodels import (
    DBDeliveryOptions,
    DBDiscount,
    DBItem,
    DBItemSnapshot,
    DBTransaction,
    DBTransactionAction,
    DBTransactionDiscount,
    DBTransactionItem,
)
from app.exceptions.exceptions import (
    ExcItemNotFound,
)
from app.utils.auth import oauth2_scheme, validate_access_token
from app.utils.configs import Settings, get_settings
from app.utils.db import (
    get_db_session,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"], route_class=APIRoute)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    # response_model=ResponseSuccess,
)
async def transaction_create(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    req_body: Annotated[
        TransactionCreate,
        Body(
            ...,
            openapi_examples={
                "example1": {
                    "summary": "Example transaction creation payload",
                    "value": {
                        "item_ids": {
                            "550e8400-e29b-41d4-a716-446655440001": 1,
                            "550e8400-e29b-41d4-a716-446655440003": 1,
                        },
                        "delivery_option_id": "13f92f95-5fe7-46b5-8893-5ea1a5eeae5a",
                        "discount_codes": ["APPLE_SALE", "ELECTRONICS_LAPTOPS_SALE"],
                    },
                }
            },
        ),
    ],
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    if req_body.discount_codes:
        query = select(DBDiscount).where(
            DBDiscount.discount_code.in_(req_body.discount_codes)
        )
        discounts_db = db.exec(query).all()
        if not discounts_db:
            raise Exception("No valid discounts found")
    else:
        discounts_db = []

    query = select(DBDeliveryOptions).where(
        DBDeliveryOptions.option_id == req_body.delivery_option_id
    )
    delivery_option_db = db.exec(query).first()
    if not delivery_option_db:
        raise Exception("Invalid delivery option")

    transaction_id = uuid.uuid4()

    transaction_items_db = []
    items_response = []
    total_price = delivery_option_db.price
    for item_id, item_count in req_body.item_ids.items():
        query = select(DBItem).where(DBItem.item_id == item_id)
        item_db = db.exec(query).first()
        if not item_db:
            raise ExcItemNotFound(item_id=item_id)
        elif item_db.stock < item_count:
            raise Exception(f"Not enough stock for item {item_id}")

        query = (
            update(DBItem)
            .where(DBItem.item_id == item_id)
            .values(stock=item_db.stock - item_count)
        )
        db.exec(query)

        query = select(DBItemSnapshot).where(
            (DBItemSnapshot.item_id == item_db.item_id)
            & (DBItemSnapshot.updated_at == item_db.updated_at)
        )
        item_snapshot_db = db.exec(query).first()
        if not item_snapshot_db:
            query = insert(DBItemSnapshot).values(item_db.model_dump(exclude={"stock"}))
            db.exec(query)

        item_price = item_db.price
        item_response = dict(
            item_id=item_db.item_id,
            name=item_db.name,
            price_unit=item_price,
            price_after_discounts=item_price,
            count=item_count,
            appied_discounts=[],
        )
        items_response.append(item_response)
        for discount in discounts_db:
            if discount.item_ids and item_db.item_id not in discount.item_ids:
                continue
            elif (
                (discount.item_ids and item_db.item_id not in discount.item_ids)
                or (discount.brands and item_db.brand not in discount.brands)
                or (discount.categories and item_db.category not in discount.categories)
                or (
                    discount.categories
                    and item_db.category in discount.categories
                    and not set(item_db.subcategories)
                    & set(discount.categories[item_db.category])
                )
            ):
                continue
            item_response["appied_discounts"].append(
                dict(
                    discount_code=discount.discount_code,
                    discount_percentage=discount.discount_percentage,
                )
            )

            item_price *= 1 - (discount.discount_percentage / 100)
        price_after_discounts = item_price.quantize(
            Decimal("0.01"), rounding=ROUND_CEILING
        )
        item_response["price_after_discounts"] = price_after_discounts
        total_price += price_after_discounts * item_count
        transaction_items_db.append(
            DBTransactionItem(
                transaction_id=transaction_id,
                item_id=item_db.item_id,
                item_updated_at=item_db.updated_at,
                count=item_count,
                price_after_discounts=price_after_discounts,
            )
        )

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
    transaction_response = transaction_db.model_dump(exclude_none=True)
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

    transaction_response = dict(
        transaction_id=transaction_db.transaction_id,
        user_id=transaction_db.user_id,
        created_at=transaction_db.created_at,
        delivery_option=delivery_option_db.name,
        delivery_price=delivery_option_db.price,
        delivery_details=transaction_db.transaction_details,
        total_price=transaction_db.total_price,
    )

    db.commit()

    transaction_response = dict(
        transaction_id=transaction_db.transaction_id,
        user_id=transaction_db.user_id,
        created_at=transaction_db.created_at,
        delivery_option=delivery_option_db.name,
        delivery_price=delivery_option_db.price,
        delivery_details=transaction_db.transaction_details,
        total_price=transaction_db.total_price,
    )

    return dict(transaction=transaction_response, transaction_items=items_response)


@router.get(
    "/current",
    status_code=status.HTTP_200_OK,
    # response_model=ResponseSuccess,
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
