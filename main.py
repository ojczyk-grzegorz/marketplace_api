import datetime as dt
from typing import Annotated, Literal

from fastapi import FastAPI, Body, Query, Path
from pydantic import BaseModel, Field

from db.db import database
from datamodels.datamodels import (
    RequestTypeItemGet,
    RequestTypeItemPut,
    ItemDetail,
    ItemStock,
    Customer,
    TransactionRequest,
    Transaction,
)
from testing import openapi_examples

app = FastAPI()


@app.get(
    "/",
    description="Health check",
)
async def root():
    return {"message": "Applictation is up and running"}


class QueryItems(BaseModel):
    subcategory: list[str] | None = None
    brand: list[str] | None = None
    type: list[str] | None = None
    material: list[str] | None = None
    color: list[str] | None = None
    pattern: list[str] | None = None
    size: list[str] | None = None
    style: list[str] | None = None
    price: tuple[float, float] = (0.01, 1_000_000.0)
    iid: int | None = None
    limit: int = Field(
        default=10,
        ge=1,
        le=30,
    )


@app.get("/items/{category}", description="Query items based on various filters")
async def read_item(
    category: str = Path(
        ...,
        title="Category of items",
    ),
    query_items: Annotated[QueryItems, Query()] = QueryItems(),
    # limit: int = Query(default=10, ge=1, le=30)
):
    query_items: dict = query_items.model_dump(exclude_none=True)
    limit: int = query_items.pop("limit")

    db_items: list[dict] = database["items"]
    items = []

    for item in db_items:
        qualified = True
        for key, value in query_items.items():
            if not qualified:
                break

            item_value = item["features"].get(key)
            if item_value is None:
                qualified = False
            elif isinstance(value, list):
                if item_value not in value:
                    qualified = False
            elif isinstance(value, tuple):
                if value[0] > item_value or item_value > value[1]:
                    qualified = False
            elif value != item_value:
                qualified = False

        if qualified:
            items.append(item)

        if len(items) >= limit:
            break

    return dict(
        q=query_items,
        items=items,
    )


# @app.post("/items", description="Route for creating item")
# async def create_item(
#     items: ItemDetail | list[ItemDetail] = Body(
#         ...,
#         openapi_examples=openapi_examples.EXAMPLE_CREATE_ITEM,
#     ),
# ):
#     if not isinstance(items, list):
#         items = [items]

#     added_items_details = {}
#     added_items_stocks = {}
#     errors_items = []

#     item_id = max(database["items_details"].keys(), default=0)
#     for item in items:
#         if not isinstance(item.name, str):
#             item = item.model_dump()
#             item["error"] = "Item name is required"
#             errors_items.append(item)
#             continue

#         item_id += 1
#         added_items_details[item_id] = item.model_dump()
#         added_items_stocks[item_id] = ItemStock().model_dump()

#     database["items_details"].update(added_items_details)
#     database["items_stocks"].update(added_items_stocks)

#     return dict(
#         added_items_details=added_items_details,
#         errors_items=errors_items,
#     )


# @app.put("/items/{request_type}", description="Route for creating item")
# async def update_item(
#     request_type: RequestTypeItemPut = Path(
#         ...,
#         title="Item PUT request type",
#     ),
#     items: list[ItemDetail] | list[ItemStock] = Body(
#         ...,
#         min_length=1,
#         max_length=30,
#         openapi_examples=openapi_examples.EXAMPLE_UPDATE_ITEM,
#     ),
# ):
#     updated_items_details = {}
#     updated_items_stocks = {}
#     errors_items = []

#     for item in items:
#         if not isinstance(item.iid, int):
#             errors_items.append(
#                 {"error": "Item should contain 'iid' value", **item.model_dump()}
#             )
#             continue

#         elif (
#             request_type is RequestTypeItemPut.details
#             and not isinstance(item, ItemDetail)
#         ) or (
#             request_type is RequestTypeItemPut.stocks
#             and not isinstance(item, ItemStock)
#         ):
#             errors_items.append(
#                 {
#                     "error": "Invalid item details for details request type",
#                     **item.model_dump(),
#                 }
#             )
#             continue

#         elif request_type is RequestTypeItemPut.details:
#             item_db = database["items_details"].get(item.iid)
#             if not item:
#                 errors_items[item.iid] = "Item not found"
#                 continue

#             item_db.update(item.model_dump(exclude_none=True))
#             updated_items_details[item.iid] = item_db

#         elif request_type is RequestTypeItemPut.stocks:
#             item_db = database["items_stocks"].get(item.iid, ItemDetail().model_dump())
#             for key, value in item.model_dump(exclude_none=True).items():
#                 item_db[key].extend(value)
#             updated_items_stocks[item.iid] = item_db

#     database["items_details"].update(updated_items_details)
#     database["items_stocks"].update(updated_items_stocks)

#     return dict(
#         updated_items_details=updated_items_details,
#         updated_items_stocks=updated_items_stocks,
#         errors_items=errors_items,
#     )


# # CUSTOMERS


# @app.get(
#     "/customer",
# )
# async def read_customer(
#     customer_ids: list[int] = Query(
#         ...,
#         title="Customers' ids",
#         description="Query to retrieve customers details based on their ids",
#         alias="customer-query",
#     ),
# ):
#     customers = {}
#     customers_errors = {}

#     for customer_id in customer_ids:
#         customer = database["customers"].get(customer_id)

#         if not customer:
#             customers_errors[customer_id] = "Customer not found"
#             continue

#         customers[customer_id] = customer

#     return dict(
#         customers=customers,
#         customers_errors=customers_errors,
#     )


# @app.get(
#     "/customers",
# )
# async def read_customers(skip: int = 0, limit: int = 10):
#     customers = dict(islice(database["customers"].items(), skip, skip + limit))

#     return customers


# @app.post("/customers", description="Route for creating item")
# async def create_customers(
#     customers: Customer | list[Customer] = Body(
#         ...,
#         openapi_examples=openapi_examples.EXAMPLE_CREATE_CUSTOMER,
#     ),
# ):
#     if not isinstance(customers, list):
#         customers = [customers]

#     added_customers = {}
#     errors_customers = []

#     customer_id = max(database["customers"], default=0)
#     emails_used = set([x["email"] for x in database["customers"].values()])
#     for customer in customers:
#         if not isinstance(customer.email, str):
#             customer = customer.model_dump()
#             customer["error"] = "Customer email required"
#             errors_customers.append(customer)
#             continue
#         elif customer.email in emails_used:
#             customer = customer.model_dump()
#             customer["error"] = "Customer email already used"
#             errors_customers.append(customer)
#             continue

#         customer_id += 1
#         customer.cid = customer_id
#         added_customers[customer_id] = customer.model_dump()

#     database["customers"].update(added_customers)

#     return dict(
#         added_customers=added_customers,
#         errors_customers=errors_customers,
#     )


# @app.put("/customers")
# async def update_customers(
#     customers: list[Customer] = Body(
#         ...,
#         min_length=1,
#         max_length=20,
#         openapi_examples=openapi_examples.EXAMPLE_UPDATE_CUSTOMER,
#     ),
# ):
#     updated_customers = {}
#     errors_items = []

#     for customer in customers:
#         if not customer.cid:
#             errors_items.append(
#                 {
#                     "error": "Customer should contain 'cid' value",
#                     **customer.model_dump(),
#                 }
#             )
#             continue

#         customer_db: dict = database["customers"].get(customer.cid)
#         if not customer_db:
#             errors_items.append(
#                 {"error": "Customer not found", **customer.model_dump()}
#             )
#             continue

#         customer_db.update(customer.model_dump(exclude_none=True))
#         updated_customers[customer.cid] = customer_db

#     return dict(
#         updated_customers=updated_customers,
#         errors_items=errors_items,
#     )


# @app.post("/transactions", description="Route for creating transactions")
# async def create_transaction(
#     transaction_requests:list[TransactionRequest] = Body(
#         ...,
#         min_length=1,
#         max_length=20,
#         openapi_examples=openapi_examples.EXAMPLE_CREATE_TRANSACTION,
#     ),
# ):
#     """
#     Create a transaction for a customer with items and amount.
#     """
#     item_stocks_updates = {}
#     transactions_created = {}
#     transactions_errors = []

#     transactions: dict = database["transactions"]
#     transaction_id = max(transactions, default=0)
#     item_stocks: dict = database["items_stocks"]

#     for transaction in transaction_requests:
#         customer = database["customers"].get(transaction_requests[0].cid)
#         if not customer:
#             transactions_errors.append(
#                 {"error": "Customer not found", **transaction.model_dump()}
#             )
#             continue

#         item_stock = item_stocks.get(transaction.iid)
#         if not item_stock:
#             transactions_errors.append(
#                 {"error": "Item not found", **transaction.model_dump()}
#             )
#             continue

#         item_stock = ItemStock.model_validate(item_stock)

#         transaction_quatity: int = transaction.quantity
#         for location in item_stock.locations:
#             quauntity = location.quantity
#             if quauntity <= transaction.quantity:
#                 transaction_quatity -= quauntity
#                 location.quantity = 0
#             else:
#                 location.quantity -= transaction.quantity
#                 transaction_quatity = 0
#                 break

#         if transaction_quatity > 0:
#             transactions_errors.append(
#                 {
#                     "error": "Not enough items in stock. Current stock: {}".format(
#                         transaction.quantity - transaction_quatity
#                     ),
#                     **transaction.model_dump(),
#                 }
#             )
#             continue

#         transaction_id += 1
#         transaction = Transaction(
#             tid=transaction_id,
#             cid=transaction.cid,
#             iid=transaction.iid,
#             quantity=transaction.quantity,
#             timestamp=dt.datetime.now(dt.timezone.utc),
#         )
#         transactions_created[transaction.tid] = transaction.model_dump()
#         item_stocks_updates[transaction.iid] = item_stock.model_dump()

#     transactions.update(transactions_created)
#     transactions.update(transactions_created)
#     item_stocks.update(item_stocks_updates)

#     return dict(
#         transactions_created=transactions_created,
#         transactions_errors=transactions_errors,
#         item_stocks_updates=item_stocks_updates,
#     )
