from uuid import uuid4
import datetime as dt

from fastapi import APIRouter, Query, Body

from db.db import database
from datamodels.response import ErrorResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/user_current", description="Get user transactions by user ID")
async def get_user_transactions_current(user_id: int = Query(...)):
    transactions_current_db = database["transactions_current"]
    items_db = database["items"]
    users_db = database["users"]

    for user in users_db:
        if user.get("uid") == user_id:
            break
    else:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )

    transactions = []
    for transaction in transactions_current_db:
        if transaction.get("buyer_id") == user_id:
            transaction_id = transaction.get("tid")
            for item in items_db:
                if item.get("transaction_id") == transaction_id:
                    transactions.append(
                        {
                            "item": item,
                            "transaction": transaction,
                        }
                    )

    return transactions


@router.post("/transaction", description="Get current transaction by item ID")
async def get_item_transaction_current(item_id: int = Query(...)):
    items_db = database["items"]
    transactions_current_db = database["transactions_current"]

    for item in items_db:
        if item.get("iid") == item_id:
            transaction_id = item.get("transaction_id")
            break
    else:
        return ErrorResponse(
            error="ITEM_NOT_FOUND",
            details={"item_id": item_id},
        )

    for transaction in transactions_current_db:
        if transaction.get("tid") == transaction_id:
            return dict(
                item=item,
                transaction=transaction,
            )

    return ErrorResponse(
        error="TRANSACTION_NOT_FOUND",
        details={"transaction_id": transaction_id},
    )


@router.post("/user_archived", description="Get user transactions by user ID")
async def get_user_transactions_archived(user_id: int = Query(...)):
    transactions_archived_db = database["transactions_archived"]
    users_db = database["users"]

    for user in users_db:
        if user.get("uid") == user_id:
            break
    else:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )

    user_uid_uuid4 = user.get("uid_uuid4")

    transactions = []
    for transaction in transactions_archived_db:
        if transaction.get("buyer_id_uuid4") == user_uid_uuid4:
            transactions.append(transaction)

    return transactions


@router.post("/create", description="Route for creating transactions")
async def create_transaction(item_id: int = Query(...), user_id: int = Query(...)):
    transactions_current_db = database["transactions_current"]
    users_db = database["users"]
    items_db = database["items"]

    for user in users_db:
        if user.get("uid") == user_id:
            break
    else:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )

    for item in items_db:
        if item.get("iid") == item_id:
            transaction_id = item.get("transaction_id")
            if transaction_id is not None:
                return ErrorResponse(
                    error="ITEM_ALREADY_IN_TRANSACTION",
                    details={"item_id": item_id},
                )
            break
    else:
        return ErrorResponse(
            error="ITEM_NOT_FOUND",
            details={"item_id": item_id},
        )

    tid = max([x["tid"] for x in transactions_current_db], default=0) + 1
    transaction = {
        "tid": tid,
        "tid_uuid4": uuid4().hex,
        "buyer_id": user_id,
        "status": "started",
        "transaction_start": dt.datetime.now().isoformat(),
        "transaction_end": None,
    }

    transactions_current_db.append(transaction)
    item["transaction_id"] = tid

    return dict(
        transaction=transaction,
        item=item,
    )


@router.post("/finalize", description="Route for creating transactions")
async def finish_transaction(
    transaction_id: int = Query(...),
    status: str = Query(..., examples=["finished", "cancelled", "expired"]),
):
    transactions_current_db = database["transactions_current"]
    transactions_archived_db = database["transactions_archived"]
    users_db = database["users"]
    items_db = database["items"]

    for nt, transaction in enumerate(transactions_current_db):
        if transaction.get("tid") == transaction_id:
            for ni, item in enumerate(items_db):
                if item.get("transaction_id") == transaction_id:
                    item["transaction_id"] = None
                    break
            else:
                transactions_current_db.pop(nt)
                return ErrorResponse(
                    error="ITEM_NOT_FOUND",
                    details={"transaction_id": transaction_id},
                )

            transaction["status"] = status
            transaction["transaction_end"] = dt.datetime.now().isoformat()
            if status == "finished":
                transaction.pop("tid", None)
                transaction["item_id_uuid4"] = item.get("iid_uuid4")
                transaction["item_snapshot"] = item
                for user in users_db:
                    if user.get("uid") == transaction.get("buyer_id"):
                        transaction["buyer_id_uuid4"] = user.get("uid_uuid4")
                        transaction["buyer_snapshot"] = user
                        transaction.pop("buyer_id", None)
                        break
                for user in users_db:
                    if user.get("uid") == item.get("seller_id"):
                        transaction["seller_id_uuid4"] = user.get("uid_uuid4")
                        transaction["seller_snapshot"] = user
                        break
                transactions_archived_db.append(transaction)
                transactions_current_db.pop(nt)
                items_db.pop(ni)

                return transaction

            else:
                item["transaction_id"] = None
                transactions_current_db.pop(nt)

            return item

    return ErrorResponse(
        error="TRANSACTION_NOT_FOUND",
        details={"transaction_id": transaction_id},
    )
