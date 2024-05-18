from fastapi import FastAPI

from db.db import get_items
from data_models.categories import Categories


app = FastAPI()


@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


@app.get("/{category}")
def get_category(category: Categories):
    return get_items(category)