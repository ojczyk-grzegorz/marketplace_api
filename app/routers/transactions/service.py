from decimal import ROUND_CEILING, Decimal
import uuid

from sqlmodel import Session, select

from app.auth.utils import validate_access_token
from app.configs.datamodels import Settings
from app.database.dbmodels import (
    DBTransaction,
    DBTransactionDiscount,
    DBTransactionFinalized,
    DBTransactionItem,
)
from app.exceptions.exceptions import ExcTransactionActiveNotFound, ExcTransactionFinalizedNotFound
from app.routers.transactions.datamodels import (
    ResponseGetAllCurrentTransactions,
    ResponseGetAllFinalizedTransactions,
    ResponseGetCurrentTransaction,
    ResponseGetFinalizedTransaction,
    TransactionCreated,
    TransactionItem,
    TransactionToCreate,
)
from app.routers.transactions.utils import (
    apply_db_discounts,
    check_for_db_item_snapshot,
    get_db_delivery_options,
    get_db_discounts,
    get_db_item,
    get_response_current_transaction,
    update_db_item_stock,
)


async def create_transaction(
    settings: Settings,
    db: Session,
    token: str,
    req_body: TransactionToCreate,
) -> ResponseGetCurrentTransaction:
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    db_discounts = get_db_discounts(db, req_body.discount_codes)
    db_delivery_options = get_db_delivery_options(db, req_body.delivery_option_id)

    transaction_id = uuid.uuid4()

    db_transaction_items = []
    transaction_items = []
    total_price = db_delivery_options.price
    for item_id, item_count in req_body.item_ids.items():
        item_db = get_db_item(db, item_id, item_count)
        update_db_item_stock(
            db,
            item_id,
            item_count,
        )
        check_for_db_item_snapshot(db, item_db)

        item_price = item_db.price
        price_after_discounts, applied_discounts = apply_db_discounts(
            item_db, item_price, db_discounts
        )

        transaction_item = TransactionItem(
            **item_db.model_dump(),
            price_unit=item_price,
            price_after_discounts=price_after_discounts,
            count=item_count,
            applied_discounts=applied_discounts,
        )
        transaction_items.append(transaction_item)

        db_transaction_item = DBTransactionItem(
            **item_db.model_dump(),
            transaction_id=transaction_id,
            count=item_count,
            price_after_discounts=price_after_discounts,
        )
        db_transaction_items.append(db_transaction_item)

        total_price += price_after_discounts * item_count

    total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    db_transaction = DBTransaction(
        **req_body.model_dump(),
        transaction_id=transaction_id,
        user_id=user_id,
        total_price=total_price,
    )
    response_transaction_details = TransactionCreated(
        **db_transaction.model_dump(),
        delivery_option=db_delivery_options.name,
        delivery_price=db_delivery_options.price,
    )
    db.add(db_transaction)

    transaction_db_discounts = [
        DBTransactionDiscount(
            transaction_id=transaction_id,
            discount_code=discount.discount_code,
        )
        for discount in db_discounts
    ]
    db.add_all(transaction_db_discounts)
    db.add_all(db_transaction_items)
    db.commit()

    return ResponseGetCurrentTransaction(
        transaction=response_transaction_details, items=transaction_items
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
    db_transactions = db.exec(query)

    delivery_options = dict()
    response_transactions = []
    for db_transaction in db_transactions:
        response_transaction = get_response_current_transaction(
            db,
            db_transaction,
            delivery_options,
        )
        response_transactions.append(response_transaction)
    return ResponseGetAllCurrentTransactions(transactions=response_transactions)


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
        (DBTransaction.user_id == user_id) & (DBTransaction.transaction_id == transaction_id)
    )
    db_transaction = db.exec(query).first()
    if not db_transaction:
        raise ExcTransactionActiveNotFound(
            transaction_id=transaction_id,
            user_id=user_id,
        )

    response_transaction = get_response_current_transaction(
        db,
        db_transaction,
    )
    return response_transaction


async def get_all_finalized_transactions(
    settings: Settings,
    db: Session,
    token: str,
) -> ResponseGetAllFinalizedTransactions:
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBTransactionFinalized).where(DBTransactionFinalized.user_id == user_id)
    db_transactions = db.exec(query)

    return ResponseGetAllFinalizedTransactions(
        transactions=[
            db_transaction.model_dump(exclude_none=True) for db_transaction in db_transactions
        ]
    )


async def get_finalized_transaction(
    settings: Settings,
    db: Session,
    token: str,
    transaction_id: uuid.UUID,
) -> ResponseGetFinalizedTransaction:
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth_secret_key,
        algorithms=[settings.auth_algorithm],
    )
    query = select(DBTransactionFinalized).where(
        (DBTransactionFinalized.user_id == user_id)
        & (DBTransactionFinalized.transaction_id == transaction_id)
    )
    db_transaction = db.exec(query).first()
    if not db_transaction:
        raise ExcTransactionFinalizedNotFound(
            transaction_id=transaction_id,
            user_id=user_id,
        )

    return ResponseGetFinalizedTransaction(transaction=db_transaction.model_dump(exclude_none=True))
