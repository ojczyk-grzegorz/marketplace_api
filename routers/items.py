from typing import Annotated
import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body

from db.db import database
from datamodels.response import ErrorResponse
from datamodels.item import (
    ItemDB,
    QueryItems,
    ItemsUser,
    ItemsQuery,
    ItemsCreate,
    ItemsCreated,
    ItemUpdate,
)
from datamodels.user import UserDb
from testing.openapi.items import ITEM_CREATE, ITEM_PATCH


router = APIRouter(prefix="/items", tags=["Items"])


@router.get(
    "/{iid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Get item by its ID",
)
async def get_item(
    iid: int = Path(
        ...,
    ),
):
    db_items: list[dict] = database["items"]
    for item_db in db_items:
        if item_db.get("iid") == iid:
            return item_db

    return ErrorResponse(
        error="ITEM_NOT_FOUND",
        details={"item_id": iid},
    )


@router.get(
    "/user/{uid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsUser | ErrorResponse,
    description="Get item by its ID",
)
async def get_item(
    uid: int = Path(
        ...,
    ),
):
    db_users: list[dict] = database["users"]
    db_items: list[dict] = database["items"]
    for user in db_users:
        if user.get("uid") == uid:
            items = []
            for item_db in db_items:
                if item_db.get("seller_id") == uid:
                    items.append(item_db)
            return ItemsUser(
                user_id=uid,
                items=items,
            )

    return ErrorResponse(
        error="USER_NOT_FOUND",
        details={"user_id": uid},
    )


@router.get(
    "/query/{category}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQuery | ErrorResponse,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    category: str = Path(
        ...,
    ),
    query_items: Annotated[QueryItems, Query()] = QueryItems(),
):
    db_items: list[dict] = database["items"]

    items = []
    features = {
        **query_items.model_dump(exclude_none=True, exclude=["limit", "features"]),
        **(query_items.features or {}),
    }

    for item in db_items:
        qualified = True
        for key, value in features.items():
            if not qualified:
                break

            item_value = item.get(key, item["features_specific"].get(key))
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

        if len(items) >= query_items.limit:
            break

    if not items:
        return ErrorResponse(
            error="ITEMS_NOT_FOUND",
            details={"query": query_items, "category": category},
        )
    return ItemsQuery(q=query_items, items=items)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ItemsCreated | ErrorResponse,
    description="Route for creating item",
)
async def create_items(
    req_body: ItemsCreate = Body(
        ...,
        openapi_examples=ITEM_CREATE,
    ),
):
    db_users: list[dict] = database["users"]
    db_items: list[dict] = database["items"]

    for seller in db_users:
        if seller.get("uid") == req_body.seller_id:
            seller = UserDb.model_validate(seller)
            break
    else:
        return ErrorResponse(
            error="SELLER_NOT_FOUND",
            details={"seller_id": req_body.seller_id},
        )

    item_id = max([x["iid"] for x in db_items], default=0)

    items = []
    for n, item in enumerate(req_body.items):
        iid = item_id + 1 + n

        item = ItemDB(
            **item.model_dump(),
            iid=iid,
            seller_id=seller.uid,
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            expires_at=(
                dt.datetime.now(dt.timezone.utc)
                + dt.timedelta(days=item.expires_at_days)
            ).isoformat(),
        )
        items.append(item)

    db_items.extend(items)
    return ItemsCreated(
        seller_id=req_body.seller_id,
        items=items,
    )


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Route for creating item",
)
async def update_items(
    item: ItemUpdate = Body(
        ...,
        openapi_examples=ITEM_PATCH,
    ),
):
    db_items: list[dict] = database["items"]

    for item_db in db_items:
        if item_db["iid"] == item.iid:
            break
    else:
        return ErrorResponse(
            error="ITEM_NOT_FOUND",
            details={"iid": item.iid},
        )

    item_db.update(
        {
            **item.model_dump(exclude_none=True),
            "updated_at": dt.datetime.now(dt.timezone.utc)
            + dt.timedelta(days=item.expires_at_days)
            if item.expires_at_days
            else item_db["updated_at"],
        }
    )

    return item_db
