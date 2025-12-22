import datetime as dt
from typing import Annotated
import uuid
from decimal import ROUND_CEILING, Decimal

from fastapi import APIRouter, Path, Body, Depends, Request, status
from fastapi.routing import APIRoute
from sqlmodel import Session, select, insert

from app.datamodels.item import ItemDB
from app.datamodels.response import ResponseSuccess
from app.datamodels.transaction import (
    TransactionCreate,
    TransactionDBIn,
    TransactionDBOut,
)
from app.datamodels.user import UserDBOutDetailed
from app.dbmodels.dbmodels import (
    DBTransaction,
    DBItem,
    DBItemSnapshot,
    DBGroundStaff,
    DBDiscount,
    DBDeliveryOptions,
    DBTransactionItem,
    DBTransactionDiscount
)
from app.exceptions.exceptions import (
    ExcItemNotFound,
    ExcUserNotFound,
)
from app.utils.auth import oauth2_scheme, validate_access_token
from app.utils.configs import Settings, get_settings
from app.utils.db import (
    db_insert,
    db_remove,
    db_search_simple,
    get_db_session_sql_model,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"], route_class=APIRoute)

# CREATE TRANSACTION
# SEE CURRENT TRANSACTIONS
# CHECK TRANSACTION STATUS
# SEE HISTORICAL TRANSACTIONS


@router.post(
    "/create/{item_id}",
    status_code=status.HTTP_200_OK,
    # response_model=ResponseSuccess,
)
async def transaction_create(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session_sql_model)],
    token: str = Depends(oauth2_scheme),
    req_body: TransactionCreate = Body(
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

    tranascation_id = uuid.uuid4()
    transaction_items_db = []
    total_price = delivery_option_db.price
    for item_id, item_count in req_body.item_ids.items():
        query = select(DBItem).where(DBItem.item_id == item_id)
        item_db = db.exec(query).first()
        if not item_db:
            raise ExcItemNotFound(item_id=item_id)
        elif item_db.stock < item_count:
            raise Exception(f"Not enough stock for item {item_id}")
        
        query = select(DBItemSnapshot).where(
            (DBItemSnapshot.item_id == item_db.item_id) & (DBItemSnapshot.updated_at == item_db.updated_at)
        )

        item_snapshot_db = db.exec(query).first()
        if not item_snapshot_db:
            query = insert(DBItemSnapshot).values(item_db.model_dump(exclude={"stock"}))
            db.exec(query)
            db.commit()
        
        item_price = item_db.price
        for discount in discounts_db:
            if discount.item_ids and not item_db.item_id in discount.item_ids:
                continue
            elif (
                (discount.item_ids and not item_db.item_id in discount.item_ids)
                or (discount.brands and not item_db.brand in discount.brands)
                or (
                    discount.categories
                    and not (item_db.category in discount.categories)
                )
                or (
                    discount.categories
                    and item_db.category in discount.categories
                    and not set(item_db.subcategories) & set(discount.categories[item_db.category])
                )
            ):
                continue
            item_price *= (1 - (discount.discount_percentage / 100))
        for _ in range(item_count):
            total_price += item_price
            transaction_items_db.append(
                DBTransactionItem(
                    transaction_id=tranascation_id,
                    item_id=item_db.item_id,
                    item_updated_at=item_db.updated_at,
                )
            )
        
    total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    transaction_db = DBTransaction(
        transaction_id=tranascation_id,
        user_id=user_id,
        delivery_option_id=req_body.delivery_option_id,
        transaction_details={
            "address": "Wawel Cathedral, Wawel, 31-001 Kraków, Poland",
        },
        total_price=total_price,
    )
    transaction_discounts_db = [
        DBTransactionDiscount(
            transaction_id=tranascation_id,
            discount_code=discount.discount_code,
        )
        for discount in discounts_db
    ]

    db.add(transaction_db)
    db.add_all(transaction_items_db)
    db.add_all(transaction_discounts_db)
    db.commit()



    return dict(transaction=transaction_db, items=transaction_items_db, discounts=discounts_db)