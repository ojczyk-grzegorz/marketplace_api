from typing import Annotated

from fastapi import APIRouter, status, Query, Path, Body
from pydantic import BaseModel, Field, ConfigDict

from db.db import database
from datamodels.response import ErrorResponse


router = APIRouter(prefix="/items", tags=["Items"])


class Item(BaseModel):
    iid: int
    city: str
    street: str
    name: str
    icon: str | None = None
    subcategory: str
    type: str
    interested: int = 0
    description: str
    delivery: list[str]
    seller_rating: float
    condition: str
    brand: str
    material: str
    color: str
    pattern: str
    size: str
    style: str
    price: float


class ItemDetails(BaseModel):
    iid: int
    seller: int
    created_at: str
    updated_at: str
    expires_at: str
    category: str
    table: str
    images: list[str] = []


class ItemResponse(BaseModel):
    item: Item
    details: ItemDetails


@router.get(
    "/{iid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemResponse | ErrorResponse,
    description="Get item by its ID",
)
async def get_item(
    iid: int = Path(
        ...,
    ),
):
    db_items: dict = database["items"]
    for detail in db_items["items"]:
        if detail.get("iid") == iid:
            for item in db_items[detail["table"]]:
                if item.get("iid") == iid:
                    return ItemResponse(
                        item=Item.model_validate(item),
                        details=ItemDetails.model_validate(detail),
                    )

    return ErrorResponse(
        error="ITEM_NOT_FOUND",
        details={"item_id": iid},
    )


class QueryItems(BaseModel):
    subcategory: list[str] | None = None
    brand: list[str] | None = None
    type: list[str] | None = None
    material: list[str] | None = None
    color: list[str] | None = None
    pattern: list[str] | None = None
    size: list[str] | None = None
    style: list[str] | None = None
    price: tuple[float, float] = (0.01, 1_000_000.0)
    iid: int | None = None
    limit: int = Field(
        default=10,
        ge=1,
        le=30,
    )


class ItemQuery(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    
    iid: int
    name: str
    price: float
    condition: str
    city: str
    street: str
    icon: str | None = None
    subcategory: str | None = None
    type: str | None = None
    interested: int = 0
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    length: str | None = None
    size: str | None = None
    style: str | None = None
    seller_rating: float = 0.0


class ItemsQueryResponse(BaseModel):
    q: QueryItems
    items: list[ItemQuery]


@router.get(
    "/query/{category}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsQueryResponse | ErrorResponse,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    category: str = Path(
        ...,
    ),
    query_items: Annotated[QueryItems, Query()] = QueryItems(),
):
    query_items: dict = query_items.model_dump(exclude_none=True)
    limit: int = query_items.pop("limit")

    db_items: list[dict] = database["items"][f"items_{category}"]

    items = []
    for item in db_items:
        qualified = True
        for key, value in query_items.items():
            if not qualified:
                break

            item_value = item.get(key)
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

        if len(items) >= limit:
            break

    if not items:
        return ErrorResponse(
            error="ITEMS_NOT_FOUND",
            details={"query": query_items, "category": category},
        )
    return ItemsQueryResponse(q=query_items, items=items)


class ItemCreate(BaseModel):
    city: str
    street: str
    name: str
    icon: str | None = None
    subcategory: str
    type: str
    interested: int = 0
    description: str
    delivery: list[str]
    condition: str
    brand: str
    material: str
    color: str
    pattern: str
    size: str
    style: str
    price: float


class ItemDetailsCreate(BaseModel):
    seller: int
    expires_at: str
    category: str
    table: str
    images: list[str] = []

class 


@router.post("", description="Route for creating item")
async def create_items(
    items: list[dict] = Body(
        ...,
        limit=1,
        openapi_examples={
            "single": {
                "summary": "single item example",
                "value": [
                    {
                        "item": {
                            "iid": 0,
                            "city": "Kielce",
                            "street": "Francuska",
                            "name": "Wilde Folk Goods Blue Boots",
                            "icon": None,
                            "subcategory": "Boots",
                            "type": "Fashion",
                            "interested": 30,
                            "description": "A versatile item that can be dressed up or down. material Leather. Lightweight and breathable for all-day comfort",
                            "delivery": ["Courier", "Postal service", "Pick-up"],
                            "seller_rating": 3.8,
                            "condition": "New",
                            "brand": "Wilde Folk Goods",
                            "material": "Leather",
                            "color": "Brown",
                            "pattern": "Floral",
                            "size": "45",
                            "style": "Knee-High Boots",
                            "price": 129.99,
                        },
                        "details": {
                            "iid": 0,
                            "seller": 162,
                            "created_at": "2025-05-07T00:00:00",
                            "updated_at": "2025-05-07T00:00:00",
                            "expires_at": "2025-05-25T00:00:00",
                            "category": "shoes",
                            "table": "items_shoes",
                            "images": [],
                        },
                    }
                ],
            },
        },
    ),
):
    db_items: list[dict] = database["items"]

    item_id = max([x["iid"] for x in db_items], default=0)
    for n, item in enumerate(items):
        item["iid"] = item_id + 1 + n

    db_items.extend(items)

    return dict(
        added_items=items,
        # errors_items=errors_items,
    )


@router.patch("", description="Route for creating item")
async def update_items(
    items: list[dict] = Body(
        ...,
        limit=1,
        openapi_examples={
            "single": {
                "summary": "single item example",
                "value": [
                    {
                        "iid": 0,
                        "seller_rating": 4.3,
                        "features": {
                            "condition": "New",
                            "brand": "Vesper Collective",
                            "material": "Denim",
                            "color": "White",
                            "pattern": "Striped",
                            "size": "XL",
                            "fit": "Regular",
                            "sleeve": "Short",
                            "collar": "V-Neck",
                            "price": 20.00,
                        },
                    }
                ],
            },
        },
    ),
):
    items_updated = []
    items_error = []

    db_items: dict = database["items"]

    for item in items:
        if not isinstance(item.get("iid"), int):
            items_error.append(
                {"error": "Item should contain 'iid' value", **item.model_dump()}
            )
            continue

        item_db = None
        for di in db_items:
            if di["iid"] == item["iid"]:
                item_db: dict = di

        if not item_db:
            items_error.append({"error": "Item not found", **item})
            continue

        item_db.update(item)
        items_updated.append(item_db)

    return dict(
        items_updated=items_updated,
        items_error=items_error,
    )
