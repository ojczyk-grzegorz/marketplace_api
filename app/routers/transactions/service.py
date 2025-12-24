from decimal import ROUND_CEILING, Decimal
import uuid

from sqlmodel import Session, select

from app.auth.utils import validate_access_token
from app.configs.datamodels import Settings
from app.database.dbmodels import (
    DBTransaction,
    DBTransactionDiscount,
    DBTransactionItem,
)
from app.routers.transactions.datamodels import (
    TransactionCreate,
    ResponseTransaction,
    ResponseTransactionDetails,
    ResponseTransactionItem,
    ResponseTransactionsCurrent,
)
from app.exceptions.exceptions import ExcTransactionActiveNotFound
from app.routers.transactions.utils import (
    apply_discounts,
    check_for_item_snapshot,
    get_delivery_option_db,
    get_discount_db,
    get_item_db,
    get_response_transaction,
    update_item_stock,
)


async def create_transaction(
    settings: Settings,
    db: Session,
    token: str,
    req_body: TransactionCreate,
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
        transaction=response_transaction_details, items=response_transaction_items
    )


async def get_all_current_transactions(
    settings: Settings,
    db: Session,
    token: str,
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBTransaction).where(DBTransaction.user_id == user_id)
    transactions_db = db.exec(query)

    delivery_options = dict()
    response_transactions = []
    for transaction_db in transactions_db:
        response_transaction = get_response_transaction(
            db,
            transaction_db,
            delivery_options,
        )
        response_transactions.append(response_transaction)
    return ResponseTransactionsCurrent(transactions=response_transactions)


async def get_current_transaction(
    settings: Settings,
    db: Session,
    token: str,
    transaction_id: uuid.UUID,
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
        raise ExcTransactionActiveNotFound(
            transaction_id=transaction_id,
            user_id=user_id,
        )

    response_transaction = get_response_transaction(
        db,
        transaction_db,
        dict(),
    )
    return response_transaction
