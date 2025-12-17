import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body, Depends, Request

from app.utils.routers import APIRouteLogging
from app.utils.configs import get_settings, Settings
from app.utils.db import get_filter
from app.utils.auth import oauth2_scheme, validate_access_token
from app.datamodels.response import ResponseSuccess
from app.exceptions.exceptions import (
    ExcItemNotFound,
    ExcUserNotFound,
    ExcInvalidExpiresAt,
)
from app.utils.db import db_search_simple, db_insert, db_update, db_remove
from app.datamodels.item import (
    ItemDB,
    ItemDBToList,
    QueryItems,
    ItemsUser,
    ItemsQuery,
)
from app.datamodels.user import UserDBOut
from tests.openapi.items import ITEM_CREATE, ITEM_PATCH, ITEM_DELETE


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
):
    settings: Settings = get_settings()

    filters = []
    for column, value in query_items.model_dump(
        exclude_none=True, exclude=["limit", "features_specific"]
    ).items():
        flt = get_filter(column, value)
        filters.append(flt)

    db_items = db_search_simple(
        table=settings.db_table_items,
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
    req: Request,
    iid: int = Path(...),
):
    settings: Settings = get_settings()
    db_items = db_search_simple(
        table=settings.db_table_items,
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