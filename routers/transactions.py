from uuid import uuid4
import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Query, status, Depends
from auth.auth import oauth2_scheme, validate_access_token, KEY, ALGORITHM

from db.db import database
from datamodels.response import ErrorResponse
from datamodels.transaction import (
    TransactionCurrentOut,
    TransationArchivedDB,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/mine",
    status_code=status.HTTP_200_OK,
    response_model=list[TransactionCurrentOut] | ErrorResponse,
    description="Get user transactions by user ID",
)
async def get_user_transactions_current(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

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
                    transaction_out = TransactionCurrentOut(
                        transaction=transaction, item=item
                    )
                    transactions.append(transaction_out)

    return transactions


@router.post(
    "/transaction",
    status_code=status.HTTP_200_OK,
    response_model=TransactionCurrentOut | ErrorResponse,
    description="Get current transaction by item ID",
)
async def get_item_transaction_current(
    token: Annotated[str, Depends(oauth2_scheme)],
    item_id: int = Query(...)
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    
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
            if transaction.get("buyer_id") != user_id:
                return ErrorResponse(
                    error="TRANSACTION_NOT_FOUND",
                    details={"transaction_id": transaction_id},
                )
            return TransactionCurrentOut(
                item=item,
                transaction=transaction,
            )

    return ErrorResponse(
        error="TRANSACTION_NOT_FOUND",
        details={"transaction_id": transaction_id},
    )


@router.post(
    "/user_archived",
    status_code=status.HTTP_200_OK,
    response_model=list[TransationArchivedDB] | ErrorResponse,
    description="Get user transactions by user ID",
)
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


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=TransactionCurrentOut | ErrorResponse,
    description="Route for creating transactions",
)
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
        "status": "pending",
        "transaction_start": dt.datetime.now().isoformat(),
        "transaction_end": None,
    }

    transactions_current_db.append(transaction)
    item["transaction_id"] = tid

    return TransactionCurrentOut(
        transaction=transaction,
        item=item,
    )


@router.post(
    "/finalize",
    status_code=status.HTTP_200_OK,
    response_model=TransactionCurrentOut | ErrorResponse,
    description="Route for creating transactions",
)
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

                return TransactionCurrentOut(
                    item=item,
                    transaction=transaction,
                )

            else:
                item["transaction_id"] = None
                transactions_current_db.pop(nt)

            return TransactionCurrentOut(
                item=item,
                transaction=transaction,
            )

    return ErrorResponse(
        error="TRANSACTION_NOT_FOUND",
        details={"transaction_id": transaction_id},
    )
