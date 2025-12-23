from decimal import ROUND_CEILING, Decimal
import uuid

from sqlmodel import Session, insert, select, update

from app.dbmodels.dbmodels import (
    DBDeliveryOptions,
    DBDiscount,
    DBItem,
    DBItemSnapshot,
)
from app.exceptions.exceptions import (
    ExcDiscountActiveNotFound,
    ExcDiscountNotFound,
    ExcInsufficientStock,
    ExcItemNotFound,
)


def get_discount_db(
    db: Session,
    discount_codes: list[DBDiscount],
):
    discounts_db = []
    if not discount_codes:
        return discounts_db
    for discount_code in discount_codes:
        query = select(DBDiscount).where(DBDiscount.discount_code == discount_code)
        discount_db = db.exec(query).first()
        if not discount_db:
            raise ExcDiscountNotFound(discount_code=discount_code)
        discounts_db.append(discount_db)
    return discounts_db


def get_delivery_option_db(
    db: Session,
    delivery_option_id: uuid.UUID,
):
    query = select(DBDeliveryOptions).where(
        DBDeliveryOptions.option_id == delivery_option_id
    )
    delivery_option_db = db.exec(query).first()
    if not delivery_option_db:
        raise ExcDiscountActiveNotFound(discount_code=delivery_option_id)
    return delivery_option_db


def get_item_db(
    db: Session,
    item_id: uuid.UUID,
    item_count: int,
):
    query = select(DBItem).where(DBItem.item_id == item_id)
    item_db = db.exec(query).first()
    if not item_db:
        raise ExcItemNotFound(item_id=item_id)
    elif item_db.stock < item_count:
        raise ExcInsufficientStock(
            item_id=item_id, requested=item_count, available=item_db.stock
        )
    return item_db


def update_item_stock(
    db: Session,
    item_id: uuid.UUID,
    item_count: int,
):
    query = (
        update(DBItem)
        .where(DBItem.item_id == item_id)
        .values(stock=(DBItem.stock - item_count))
    )
    db.exec(query)


def check_for_item_snapshot(
    db: Session,
    item_db: DBItem,
):
    query = select(DBItemSnapshot).where(
        (DBItemSnapshot.item_id == item_db.item_id)
        & (DBItemSnapshot.updated_at == item_db.updated_at)
    )
    item_snapshot_db = db.exec(query).first()
    if not item_snapshot_db:
        query = insert(DBItemSnapshot).values(item_db.model_dump(exclude={"stock"}))
        db.exec(query)


def apply_discounts(
    item_db: DBItem,
    item_price: Decimal,
    discounts_db: list[DBDiscount],
) -> tuple[Decimal, list[dict]]:
    applied_discounts = []
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
        applied_discounts.append(
            dict(
                discount_code=discount.discount_code,
                discount_percentage=discount.discount_percentage,
            )
        )

        item_price *= 1 - (discount.discount_percentage / 100)
    price_after_discounts = item_price.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    return price_after_discounts, applied_discounts
