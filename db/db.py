from pydantic import BaseModel, UUID4, Field
from uuid import uuid4
from pydantic import BaseModel, UUID4, Field, field_validator, ValidationError
from typing import Annotated
from annotated_types import MinLen, MaxLen


CATEGORIES_SCHEMA =  {
    'activities': set(),
    'clothes': set(),
    'electronics': {'laptop', 'phone', 'tablet'},
    'estates': set(),
    'farming': set(),
    'other': set(),
    'services': {'cleaning', 'renovation'},
    'vehicles': {'bicycle', 'car', 'cart', 'motor'}
}

 

class Item(BaseModel):
    name: str
    description: str | None = None
    post: str | None = None
    categories: Annotated[dict, MinLen(1), MaxLen(2)]

    @field_validator("categories", mode="after")
    @classmethod
    def check_types(cls, value):
        for cat, subcats in value.items():
            len(set(subcats) - CATEGORIES_SCHEMA[cat]) == 0


class ItemDb(Item):
    id: str | UUID4 = Field(default_factory=uuid4)



def create_items_db(item: Item):
    db_item = ItemDb.model_validate(item.model_dump())
    items.append(db_item)

    return db_item


def get_items_db():
    return items


def get_items_categories(categories: set[str], strict: bool = True) -> list:
    if strict:    
        return [
            item for item in items
            if len(categories - item.categories) == 0
        ]
    
    return [
        item for item in items
        if len(categories - item.categories) < len(item.categories)
    ]

items = [
    ItemDb(id=uuid4(), name="Skoda Fabia", categories={"vehicles": ["car"]}),
    ItemDb(id=uuid4(), name="BMW x55", categories={"vehicles": ["car"]}),
    ItemDb(id=uuid4(), name="Tesla 4", categories={"vehicles": ["car"]}),
    ItemDb(id=uuid4(), name="Lenovo ThinkPad U14 Gen. 3", categories={"electronics": ["laptop"]}),
    ItemDb(id=uuid4(), name="Samsung S23", categories={"electronics": ["phone"]}),
    ItemDb(id=uuid4(), name="iPad Air 5 64", categories={"electronics": ["tablet"]}),
    ItemDb(id=uuid4(), name="Office cleaning Los Angeles", categories={"services": ["cleaning"]}),
    ItemDb(id=uuid4(), name="Apartment renovation New York", categories={"services": ["renovation"]}),
    ItemDb(id=uuid4(), name="Dog walking Denver", categories={"services": ["other"]})
]