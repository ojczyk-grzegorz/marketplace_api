from typing import Annotated

from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field

from db.db import database


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get(
    "/{transaction_id}",
)
async def get_transaction(
    transaction_id: int = Path(
        ...,
    ),
):
    transaction = None
    transaction_errors = []

    for t in database["transactions"]:
        if t.get("tid") == transaction_id:
            transaction = t
            break
    else:
        transaction_errors.append("Transaction not found")

    return dict(transaction=transaction, transaction_errors=transaction_errors)


@router.post("", description="Route for creating transactions")
async def create_transaction(
    transaction: dict = Body(
        ...,
        openapi_examples={
            "good": {
                "value": {
                    "iid": 4999,
                    "name": "Wilde Folk Goods Purple Trousers",
                    "seller": 484,
                    "date": "2025-03-01T00:00:00",
                    "buyer": 906,
                    "item": {
                        "iid": 4999,
                        "created_at": "2025-02-20T00:00:00",
                        "expires_at": "2025-03-12T00:00:00",
                        "seller": 484,
                        "city": "P\u0142ock",
                        "name": "Wilde Folk Goods Purple Trousers",
                        "category": "clothes",
                        "subcategory": "Trousers",
                        "type": "Fashion",
                        "interested": 14,
                        "images": [],
                        "description": "A unique blend of textures and materials for a standout look.\nprice - 45.99.\nA piece that combines comfort and sophistication.\nraise - High.\nA piece that tells a story with its design and materials.\nbrand - Wilde Folk Goods.\nA unique blend of textures and materials for a standout look.\nraise - High.\nPerfect for casual outings or lounging at home.\ncondition - Fair.\nA stylish and comfortable piece for everyday wear",
                        "delivery": ["Parcel box", "Postal service"],
                        "seller_rating": 4.0,
                        "features": {
                            "condition": "Fair",
                            "brand": "Wilde Folk Goods",
                            "material": "Linen",
                            "color": "Purple",
                            "pattern": "Solid",
                            "size": "S",
                            "length": "Long",
                            "fit": "Slim",
                            "shape": "Skinny",
                            "raise": "High",
                            "price": 45.99,
                        },
                    },
                },
            },
        },
    ),
):
    """
    Create a transaction for a customer with items and amount.
    """

    transaction_errors = []

    db_transactions = database["transactions"]
    transaction["tid"] = max([x["tid"] for x in db_transactions], default=0) + 1
    db_transactions.append(transaction)

    return dict(
        transaction=transaction,
        transaction_errors=transaction_errors,
    )
