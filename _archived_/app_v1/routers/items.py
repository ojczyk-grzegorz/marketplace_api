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
        f"LIMIT {query_items.limit}",
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


@router.post(
    "/mine",
    status_code=status.HTTP_200_OK,
    response_model=ItemsUser | ErrorResponse,
    description="Get item by its ID",
)
async def get_user_items(token: str = Depends(oauth2_scheme)):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    resp = get_user_items(user_id)
    return resp


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Route for creating an item",
)
async def create_items(
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
        UserOut.model_fields.keys(),
        f"uid = {user_id}",
    )

    if not users:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )

    item = ItemDB(
        **item.model_dump(),
        seller_id=user_id,
        created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        expires_at=(
            dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=item.expires_at_days)
        ).isoformat(),
    ).model_dump(exclude_none=True, mode="json")

    item: dict = db_insert("items", item, ItemDB.model_fields.keys())
    return item


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Route for patching an item",
)
async def update_item(
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
    now = dt.datetime.now(dt.timezone.utc)
    expires_at = (
        now + dt.timedelta(days=item.expires_at_days) if item.expires_at_days else None
    )
    item_id = item.iid
    item = ItemDB(
        **item.model_dump(),
        seller_id=user_id,
        updated_at=now.isoformat(),
        expires_at=expires_at.isoformat() if expires_at else None,
    ).model_dump(exclude_none=True, mode="json")

    item: dict = db_update(
        "items",
        item,
        f"seller_id = {user_id} AND iid = {item_id}",
        ItemDB.model_fields.keys(),
    )

    if not item:
        return ErrorResponse(
            error="ITEM_NOT_FOUND",
            details={"item_id": item_id},
        )

    return item


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    response_model=list[dict] | ErrorResponse,
    description="Route for deleting an item",
)
async def remove_item(
    token: str = Depends(oauth2_scheme), req_body: ItemsRemove = Body(...)
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

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
    items = db_remove(
        "items",
        f"seller_id = {user_id} AND iid IN ({', '.join(str(x) for x in req_body.item_ids)})",
        columns_out=["iid", "name"],
    )
    return items
