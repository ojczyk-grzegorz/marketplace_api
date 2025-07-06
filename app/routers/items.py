import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body, Depends, Request

from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.db import get_filter
from app.utils.auth import oauth2_scheme, validate_access_token
from app.datamodels.response import ResponseSuccess
from app.exceptions.exceptions import ExcItemNotFound, ExcUserNotFound, ExcInvalidExpiresAt
from app.utils.db import db_search_simple, db_insert, db_update, db_remove
from app.datamodels.item import (
    ItemDB,
    ItemDBToList,
    QueryItems,
    ItemsUser,
    ItemsQuery,
    ItemCreate,
    ItemUpdate,
    ItemRemove,
)
from app.datamodels.user import UserDBOut
from app.testing.openapi.items import ITEM_CREATE, ITEM_PATCH, ITEM_DELETE


router = APIRouter(prefix="/items", tags=["Items"], route_class=APIRouteLogging)


@router.get(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQuery,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    req: Request,
    query_items: QueryItems = Query(QueryItems()),
    settings: Settings = Depends(get_settings),
):
    filters = []
    for column, value in query_items.model_dump(
        exclude_none=True, exclude=["limit", "features_specific"]
    ).items():
        flt = get_filter(column, value)
        filters.append(flt)

    db_items = db_search_simple(
        table=settings.database.tables.items.name,
        columns=ItemDBToList.model_fields.keys(),
        where=" AND ".join(filters),
        other=f"LIMIT {query_items.limit}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "get"],
        ),
    )

    return ItemsQuery(
        q=query_items,
        items=db_items,
    )


@router.get(
    "/item/{iid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB,
    description="Get item by its ID",
)
async def get_item(
    req: Request, iid: int = Path(...), settings: Settings = Depends(get_settings)
):
    db_items = db_search_simple(
        table=settings.database.tables.items.name,
        columns=ItemDB.model_fields.keys(),
        where=f"iid = {iid}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "get"],
        ),
    )

    if not db_items:
        raise ExcItemNotFound(item_id=iid)
    return db_items[0]


@router.get(
    "/user/{uid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsUser,
    description="Get item by its ID",
)
async def get_user_items(
    req: Request, uid: int = Path(...), settings: Settings = Depends(get_settings)
):
    users = db_search_simple(
        table=settings.database.tables.users.name,
        columns=UserDBOut.model_fields.keys(),
        where=f"uid = {uid}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["users", "get"],
        ),
    )
    if not users:
        raise ExcUserNotFound(user_id=uid)

    db_items = db_search_simple(
        table=settings.database.tables.items.name,
        columns=ItemDBToList.model_fields.keys(),
        where=f"seller_id = {uid}",
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "get"],
        ),
    )

    return ItemsUser(user=users[0], items=db_items)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
    description="Route for creating an item",
)
async def item_create(
    req: Request,
    token: str = Depends(oauth2_scheme),
    item: ItemCreate = Body(
        ...,
        openapi_examples=ITEM_CREATE,
    ),
    settings: Settings = Depends(get_settings),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth.secret_key,
        algorithms=[settings.auth.algorithm],
    )

    created_at = dt.datetime.now(dt.timezone.utc)
    if item.expires_at <= created_at:
        raise ExcInvalidExpiresAt(expires_at=item.expires_at)

    item = ItemDB(
        **item.model_dump(),
        seller_id=user_id,
        created_at=created_at,
        updated_at=created_at,
    ).model_dump(exclude_none=True, mode="json")

    db_items: dict = db_insert(
        table=settings.database.tables.items.name,
        data=item,
        columns_out=ItemDB.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "create"],
        ),
    )
    return ResponseSuccess(
        message="Item created successfully",
        details={
            "item": db_items[0],
        },
    )


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
    description="Route for patching an item",
)
async def item_update(
    req: Request,
    token: str = Depends(oauth2_scheme),
    item: ItemUpdate = Body(
        ...,
        openapi_examples=ITEM_PATCH,
    ),
    settings: Settings = Depends(get_settings),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth.secret_key,
        algorithms=[settings.auth.algorithm],
    )

    updated_at = dt.datetime.now(dt.timezone.utc)
    if item.expires_at <= updated_at:
        raise ExcInvalidExpiresAt(expires_at=item.expires_at)

    item = ItemDB(
        **item.model_dump(),
        updated_at=dt.datetime.now(dt.timezone.utc),
    )

    item_id = item.iid
    db_items = db_update(
        table=settings.database.tables.items.name,
        data=item.model_dump(exclude_none=True, mode="json"),
        where=f"iid = '{item_id}' AND seller_id = {user_id}",
        columns_out=ItemDB.model_fields.keys(),
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "update"],
        ),
    )
    if not db_items:
        raise ExcItemNotFound(item_id=item_id, user_id=user_id)
    return ResponseSuccess(
        message="Item updated successfully",
        details={
            "item": db_items[0],
        },
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSuccess,
    description="Route for deleting an item",
)
async def item_remove(
    req: Request,
    token: str = Depends(oauth2_scheme),
    req_body: ItemRemove = Body(..., openapi_examples=ITEM_DELETE),
    settings: Settings = Depends(get_settings),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=settings.auth.secret_key,
        algorithms=[settings.auth.algorithm],
    )

    db_items = db_remove(
        table=settings.database.tables.items.name,
        where=f"seller_id = {user_id} AND iid = {req_body.item_id}",
        columns_out=["iid", "name"],
        log_kwargs=dict(
            request_id=req.uuid4,
            query_tags=["items", "remove"],
        ),
    )
    if not db_items:
        raise ExcItemNotFound(item_id=req_body.item_id, user_id=user_id)
    return ResponseSuccess(
        message="Item removed successfully",
        details={
            "item": db_items[0],
        },
    )
