from typing import Annotated
import uuid

from fastapi import Depends, Path
from sqlmodel import Session, select

from app.database.dbmodels import DBItem
from app.database.utils import get_db_session
from app.routers.items.datamodels import ItemQuery, ResponseFilterItems, ResponseRetrieveItem
from app.exceptions.exceptions import ExcItemNotFound


async def filter_items(
    item_query: ItemQuery,
    db: Session,
):
    query = select(DBItem)
    if item_query.search:
        query = query.where(
            DBItem.name.ilike(f"%{item_query.search}%")
            | DBItem.description.ilike(f"%{item_query.search}%")
        )
    if item_query.category:
        query = query.where(DBItem.category == item_query.category)
    if item_query.subcategory:
        query = query.where(DBItem.subcategories.contains(item_query.subcategory))
    if item_query.price:
        if item_query.price[0]:
            query = query.where(DBItem.price >= item_query.price[0])
        if item_query.price[1]:
            query = query.where(DBItem.price <= item_query.price[1])
    if item_query.brand:
        query = query.where(DBItem.brand == item_query.brand)

    return ResponseFilterItems(
        items=[x.model_dump() for x in db.exec(query)],
    )


async def retrieve_item(
    db: Annotated[Session, Depends(get_db_session)],
    item_id: Annotated[uuid.UUID, Path(...)],
):
    query = select(DBItem).where(DBItem.item_id == item_id)
    item = db.exec(query).first()
    if not item:
        raise ExcItemNotFound(item_id=item_id)
    return ResponseRetrieveItem(item=item.model_dump())
