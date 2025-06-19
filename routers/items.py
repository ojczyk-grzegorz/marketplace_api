from typing import Annotated

from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field

from db.db import database


router = APIRouter(prefix="/items", tags=["Items"])


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


@router.get("/{category}", description="Query items based on various filters")
async def get_items(
    category: str = Path(
        ...,
        title="Category of items",
    ),
    query_items: Annotated[QueryItems, Query()] = QueryItems(),
    # limit: int = Query(default=10, ge=1, le=30)
):
    query_items: dict = query_items.model_dump(exclude_none=True)
    limit: int = query_items.pop("limit")

    db_items: list[dict] = database["items"]
    items = []

    for item in db_items:
        if item.get("category", "").lower() != category.lower():
            continue

        qualified = True
        for key, value in query_items.items():
            if not qualified:
                break

            if key == "iid" and item.get("iid") == value:
                continue

            item_value = item["features"].get(key)
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

    return dict(
        q=query_items,
        items=items,
    )


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
                        "name": "Black jeans",
                        "category": "clothes",
                        "seller": 300,
                        "city": "P\u0142ock",
                        "subcategory": "T-Shirt",
                        "type": "Fashion",
                        "interested": 28,
                        "images": [],
                        "description": "Made with sustainable practices in mind.\nprice - 15.99.\nA classic design with a contemporary twist.\nbrand - Kinetic Stitch.\nA must-have addition to any wardrobe.\npattern - Striped.\nIdeal for layering or wearing on its own",
                        "delivery": ["Pick-up", "Courier", "Courier", "Parcel box"],
                        "seller_rating": 3.7,
                        "features": {
                            "price": 79.99,
                            "condition": "Fair",
                            "brand": "Kinetic Stitch",
                            "material": "Leather",
                            "color": "Purple",
                            "pattern": "Striped",
                            "size": "S",
                            "fit": "Loose",
                            "sleeve": "Long",
                            "collar": "Crew",
                        },
                    }
                ],
            },
        },
    ),
):
    # added_items_details = {}
    # added_items_stocks = {}
    # errors_items = []
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
