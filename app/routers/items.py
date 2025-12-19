from typing import Annotated

from fastapi import APIRouter, status, Query, Path, Depends
from fastapi.routing import APIRoute

from sqlmodel import Session, select
import uuid

from app.utils.db import get_db_session_sql_model
from app.datamodels.item import (
    Item,
    QueryItemMultiple,
    QueryItemSingle,
)

from app.dbmodels.dbmodels import ItemSQL


router = APIRouter(prefix="/items", tags=["Items"], route_class=APIRoute)


@router.get(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=QueryItemMultiple,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    query_items: Annotated[Item, Query()],
    db: Annotated[Session, Depends(get_db_session_sql_model)],
):
    query = select(ItemSQL)
    if query_items.search:
        query = query.where(
            ItemSQL.name.ilike(f"%{query_items.search}%")
            | ItemSQL.description.ilike(f"%{query_items.search}%")
        )
    if query_items.category:
        query = query.where(ItemSQL.category == query_items.category)
    if query_items.subcategory:
        query = query.where(ItemSQL.subcategories.contains(query_items.subcategory))
    if query_items.price:
        if query_items.price[0]:
            query = query.where(ItemSQL.price >= query_items.price[0])
        if query_items.price[1]:
            query = query.where(ItemSQL.price <= query_items.price[1])
    if query_items.brand:
        query = query.where(ItemSQL.brand == query_items.brand)

    return QueryItemMultiple(
        q=query_items,
        items=[x.model_dump() for x in db.exec(query)],
    )


@router.get(
    "/item/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=QueryItemSingle,
    description="Get item by its ID",
)
async def get_item(
    db: Annotated[Session, Depends(get_db_session_sql_model)],
    item_id: uuid.UUID = Path(...),
):
    query = select(ItemSQL).where(ItemSQL.item_id == item_id)
    item = db.exec(query).first()
    return QueryItemSingle(
        item_id=item_id,
        item=item.model_dump() if item else None,
    )
