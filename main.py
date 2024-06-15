from fastapi import FastAPI
from pymongo import MongoClient

from db.db import Item, get_items_db, get_items_categories, create_items_db, CATEGORIES_SCHEMA

app = FastAPI()


@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


@app.get("/items")
def get_items():
    # return get_items_db()
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["marketplaceApi"]
        collection = db["items"]
        results: list = list(collection.find().)
    return str(results)


@app.post("/create_items")
def create_items():
    item = {}
    return create_items_db(item)


@app.get("/categories")
def get_categories():
    return []