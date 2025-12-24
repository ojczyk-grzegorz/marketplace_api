from decimal import ROUND_CEILING, Decimal
import uuid

from sqlmodel import Session, insert, select, update

from app.database.dbmodels import (
    DBDeliveryOptions,
    DBDiscount,
    DBItem,
    DBItemSnapshot,
    DBTransaction,
    DBTransactionAction,
    DBTransactionItem,
)
from app.exceptions.exceptions import (
    ExcDiscountActiveNotFound,
    ExcInsufficientStock,
    ExcItemNotFound,
)
from app.routers.transactions.datamodels import (
    ResponseGetCurrentTransaction,
    TransactionAction,
    TransactionCreated,
    TransactionItem,
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
            raise ExcDiscountActiveNotFound(discount_code=discount_code)
        discounts_db.append(discount_db)
    return discounts_db


def get_delivery_option_db(
    db: Session,
    delivery_option_id: uuid.UUID,
):
    query = select(DBDeliveryOptions).where(DBDeliveryOptions.option_id == delivery_option_id)
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
        raise ExcInsufficientStock(item_id=item_id, requested=item_count, available=item_db.stock)
    return item_db


def update_item_stock(
    db: Session,
    item_id: uuid.UUID,
    item_count: int,
):
    query = (
        update(DBItem).where(DBItem.item_id == item_id).values(stock=(DBItem.stock - item_count))
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
                and not set(item_db.subcategories) & set(discount.categories[item_db.category])
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


def get_response_transaction(
    db: Session,
    transaction_db: DBTransaction,
    delivery_options: dict[uuid.UUID, DBDeliveryOptions] = dict(),
):
    delivery_option = delivery_options.get(transaction_db.delivery_option_id)
    if not delivery_option:
        query = select(DBDeliveryOptions).where(
            DBDeliveryOptions.option_id == transaction_db.delivery_option_id
        )
    delivery_option_db = db.exec(query).first()
    query = select(DBTransactionItem).where(
        DBTransactionItem.transaction_id == transaction_db.transaction_id
    )
    transaction_items_db = db.exec(query)

    response_transaction_items = []
    for transaction_item_db in transaction_items_db:
        query = select(DBItemSnapshot).where(DBItemSnapshot.item_id == transaction_item_db.item_id)
        item_db = db.exec(query).first()
        response_transaction_item = TransactionItem(
            **item_db.model_dump(),
            **transaction_item_db.model_dump(exclude={"item_id"}),
            price_unit=item_db.price,
        )
        response_transaction_items.append(response_transaction_item)

    response_transaction_actions = []
    query = select(DBTransactionAction).where(
        DBTransactionAction.transaction_id == transaction_db.transaction_id
    )
    transaction_actions_db = db.exec(query)
    for transaction_action_db in transaction_actions_db:
        response_transaction_action = TransactionAction(
            action=transaction_action_db.action,
            description=transaction_action_db.description,
            performed_at=transaction_action_db.performed_at,
        )
        response_transaction_actions.append(response_transaction_action)

    response_transaction_details = TransactionCreated(
        **transaction_db.model_dump(),
        **delivery_option_db.model_dump(exclude={"name"}),
        delivery_option=delivery_option_db.name,
        delivery_price=delivery_option_db.price,
    )
    return ResponseGetCurrentTransaction(
        transaction=response_transaction_details,
        items=response_transaction_items,
        actions=response_transaction_actions,
    )
