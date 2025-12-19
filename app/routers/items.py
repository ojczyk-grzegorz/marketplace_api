from typing import Annotated

from fastapi import APIRouter, status, Query, Path, Request, Depends
from fastapi.routing import APIRoute

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.utils.configs import get_settings, Settings
from app.utils.db import get_filter, get_db_session
from app.exceptions.exceptions import (
    ExcItemNotFound,
)
from app.utils.db import db_search_simple
from app.datamodels.item import (
    Item,
    ItemDB,
    ItemDBToList,
    QueryItems,
    ItemsQuery,
)


router = APIRouter(prefix="/items", tags=["Items"], route_class=APIRoute)

# QUERY ITEMS
# GET ITEM BY ID


@router.get(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQuery,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    query_items: Annotated[Item, Query()],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
):
    q = query_items.model_dump(exclude_none=True, mode="json")
    db_items_matching = db.execute(
        text(
            "SELECT "
            + ", ".join(q.keys())
            + " FROM " + settings.db_table_items
            + " WHERE "
            + " AND".join([f" {key} = :{key}" for key in q.keys()])
        ),
        params=q,
    ).fetchall()


    return ItemsQuery(
        q=query_items,
        items=[x._mapping for x in db_items_matching],
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
