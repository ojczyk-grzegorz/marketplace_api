from fastapi import FastAPI

from db.db import get_items
from data_models.categories import (
    Categories,
    Item,
    get_category_models
)


app = FastAPI()


@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


@app.get("/{category}")
def get_category_items(category: Categories):
    return get_items(category)


@app.post("/{category}/create_item")
def post_category_create_item(category: Categories, item: Item):
    item_model: Item = get_category_models(category).item_model
    item: Item = item_model.model_validate(item.model_dump())
    
    items: list = get_items(category)
    items.append(item)

    return item