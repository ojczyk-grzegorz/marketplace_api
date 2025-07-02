import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body, Depends
from auth.auth import oauth2_scheme, validate_access_token, KEY, ALGORITHM

from db.db import db_search_simple, db_insert, db_update, db_remove
from datamodels.response import ErrorResponse
from datamodels.item import (
    ItemDB,
    ItemDBToList,
    QueryItems,
    ItemsUser,
    ItemsQuery,
    ItemCreate,
    ItemUpdate,
    ItemRemove,
)
from datamodels.user import UserDBOut
from testing.openapi.items import ITEM_CREATE, ITEM_PATCH, ITEM_DELETE


router = APIRouter(prefix="/items", tags=["Items"])


def get_query_value(value):
    if isinstance(value, str):
        return f"'{value}'"
    else:
        return str(value)


@router.get(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQuery | ErrorResponse,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    query_items: QueryItems = Query(QueryItems()),
):
    filters = []
    for key, value in query_items.model_dump(
        exclude_none=True, exclude=["limit", "features_specific"]
    ).items():
        if isinstance(value, list):
            flt = f"{key} IN ({', '.join(get_query_value(x) for x in value)})"
        elif isinstance(value, tuple):
            flt = f"{key} BETWEEN {get_query_value(value[0])} AND {get_query_value(value[1])}"
        else:
            flt = f"{key} = {get_query_value(value)}"

        filters.append(flt)

    items = db_search_simple(
        "items",
        ItemDBToList.model_fields.keys(),
        " AND ".join(filters),
        f"LIMIT {query_items.limit}",
    )

    return ItemsQuery(
        q=query_items,
        items=items,
    )


@router.get(
    "/item/{iid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Get item by its ID",
)
async def get_item(iid: int = Path(...)):
    items = db_search_simple(
        "items",
        ItemDB.model_fields.keys(),
        f"iid = {iid}",
    )

    if items:
        return items[0]

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
async def get_user_items(uid: int = Path(...)):
    users = db_search_simple(
        "users",
        UserDBOut.model_fields.keys(),
        f"uid = {uid}",
    )
    if not users:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": uid},
        )
    items = db_search_simple(
        "items",
        ItemDBToList.model_fields.keys(),
        f"seller_id = {uid}",
    )

    return ItemsUser(user=users[0], items=items)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Route for creating an item",
)
async def item_create(
    token: str = Depends(oauth2_scheme),
    item: ItemCreate = Body(
        ...,
        openapi_examples=ITEM_CREATE,
    ),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )
    users = db_search_simple(
        "users",
        UserDBOut.model_fields.keys(),
        f"uid = {user_id}",
    )
    if not users:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )

    created_at = dt.datetime.now(dt.timezone.utc)
    if item.expires_at <= created_at:
        return ErrorResponse(
            error="INVALID_EXPIRES_AT",
            details={
                "expires_at": item.expires_at,
                "message": "Expiration date must be in the future.",
            },
        )

    item = ItemDB(
        **item.model_dump(),
        seller_id=user_id,
        created_at=created_at,
        updated_at=created_at,
    ).model_dump(exclude_none=True, mode="json")

    items: dict = db_insert("items", item, ItemDB.model_fields.keys())
    return items[0]


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Route for patching an item",
)
async def item_update(
    token: str = Depends(oauth2_scheme),
    item: ItemUpdate = Body(
        ...,
        openapi_examples=ITEM_PATCH,
    ),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    updated_at = dt.datetime.now(dt.timezone.utc)
    if item.expires_at <= updated_at:
        return ErrorResponse(
            error="INVALID_EXPIRES_AT",
            details={
                "expires_at": item.expires_at,
                "message": "Expiration date must be in the future.",
            },
        )

    item = ItemDB(
        **item.model_dump(),
        updated_at=dt.datetime.now(dt.timezone.utc),
    )

    item_id = item.iid
    items = db_update(
        "items",
        item.model_dump(exclude_none=True, mode="json"),
        f"iid = '{item_id}' AND seller_id = {user_id}",
        ItemDB.model_fields.keys(),
    )
    if not items:
        return ErrorResponse(
            error="ITEM_NOT_FOUND",
            details={"item_id": item_id, "user_id": user_id},
        )
    return items[0]


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    response_model=dict | ErrorResponse,
    description="Route for deleting an item",
)
async def item_remove(
    token: str = Depends(oauth2_scheme),
    req_body: ItemRemove = Body(..., openapi_examples=ITEM_DELETE),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    items = db_remove(
        "items",
        f"seller_id = {user_id} AND iid = {req_body.item_id}",
        columns_out=["iid", "name"],
    )
    if not items:
        return ErrorResponse(
            error="ITEMS_NOT_FOUND",
            details={"item_ids": req_body.item_id, "user_id": user_id},
        )
    return items[0]
