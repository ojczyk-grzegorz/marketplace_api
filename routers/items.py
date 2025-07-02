import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body, Depends
from auth.auth import oauth2_scheme, validate_access_token, KEY, ALGORITHM

from db.db import database, db_query, db_search_simple, db_insert, db_update, db_remove
from datamodels.response import ErrorResponse
from datamodels.item import (
    ItemDB,
    ItemDBToList,
    QueryItems,
    ItemsUser,
    ItemsQuery,
    ItemCreate,
    ItemUpdate,
    ItemsRemove,
)
from datamodels.user import UserOut
from testing.openapi.items import ITEM_CREATE, ITEM_PATCH


router = APIRouter(prefix="/items", tags=["Items"])


def get_user_items(user_id: int):
    users = db_search_simple(
        "users",
        UserOut.model_fields.keys(),
        f"uid = {user_id}",
    )
    if not users:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )
    items = db_search_simple(
        "items",
        ItemDBToList.model_fields.keys(),
        f"seller_id = {user_id}",
    )

    return ItemsUser(user=users[0], items=items)


def get_query_value(value):
    if isinstance(value, str):
        return f"'{value}'"
    else:
        return str(value)


@router.get(
    "/query/{category}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQuery | ErrorResponse,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    category: str = Path(...), 
    query_items: QueryItems = Query(QueryItems()),
):
    category_ids = db_search_simple(
        "categories",
        ["cid"],
        f"name = '{category}'",
    )
    if not category_ids:
        return ErrorResponse(
            error="CATEGORY_NOT_FOUND",
            details={"category": category},
        )
    category_id = category_ids[0]["cid"]

    features_specific = {
        **query_items.model_dump(
            exclude_none=True, exclude=["limit", "features_specific"]
        ),
        **(query_items.features_specific or {}),
    }

    filters = []
    for key, value in features_specific.items():
        if isinstance(value, list):
            flt = f"{key} IN ({', '.join(get_query_value(x) for x in value)})"
        elif isinstance(value, tuple):
            flt = f"{key} BETWEEN {get_query_value(value[0])} AND {get_query_value(value[1])}"
        else:
            flt = f"{key} = {get_query_value(value)}"

        filters.append(flt)
    if filters:
        filter_str = " AND ".join(filters)
    
    items = db_search_simple(
        "items",
        ItemDBToList.model_fields.keys(),
        f"category_id = {category_id} AND ({filter_str})",
        f"LIMIT {query_items.limit}"
    )

    return ItemsQuery(
        q=query_items,
        items=items,
    )


@router.get(
    "/{iid}",
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
    resp = get_user_items(uid)
    return resp
