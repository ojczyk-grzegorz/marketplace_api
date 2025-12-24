from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.routing import APIRoute
from sqlmodel import Session

from app.database.utils import get_db_session
from app.routers.items.datamodels import (
    ItemQuery,
    ResponseFilterItems,
    ResponseRetrieveItem,
)
from app.routers.items.service import filter_items, retrieve_item
from development.openapi_examples import get_filter_items_examples, get_retrieve_item_examples

router = APIRouter(prefix="/items", tags=["Items"], route_class=APIRoute)


@router.get(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ResponseFilterItems,
    response_model_exclude_none=True,
    description="Query items based on various filters",
)
async def req_filter_items(
    db: Annotated[Session, Depends(get_db_session)],
    item_query: Annotated[ItemQuery, Query(openapi_examples=get_filter_items_examples())],
):
    return await filter_items(item_query=item_query, db=db)


@router.get(
    "/item/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseRetrieveItem,
    response_model_exclude_none=True,
    description="Get item by its ID",
)
async def req_retrieve_item(
    db: Annotated[Session, Depends(get_db_session)],
    item_id: Annotated[uuid.UUID, Path(..., openapi_examples=get_retrieve_item_examples())],
):
    return await retrieve_item(db=db, item_id=item_id)
