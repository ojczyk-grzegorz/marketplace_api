from fastapi import FastAPI

from db.db import Item, get_items_all, get_items_categories, add_item, CATEGORIES_SCHEMA

# Use Field(... class from pydantic (pt 8)
# Use Body (pt11), Body(..., embed=True) class from pydantic (pt 8)
# Add images (pt9 )
# Add examples of requests pt 10 with model_config
app = FastAPI()


@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


# TODO: Add query (pt: 5, 6, 7)
# Param's query as a standard query / filter for db searches (for GET, POST, PUT, ...)
# U can add query attr to returned item to keep info on condition it was retrieved
# Use Query class from fastapi to standarize it
# Use Query(...

@app.get("/items")
def get_category_items():
    return get_items_all()


@app.get("/items/{category}")
def get_category_items(category: str):
    if category not in CATEGORIES_SCHEMA:
        return {"message": "category unknown"}

    return get_items_categories({category}, strict=False)


@app.post("/create_item")
def post_category_create_item(item: Item):
    return add_item(item)