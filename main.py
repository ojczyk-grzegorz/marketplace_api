from fastapi import FastAPI
from pymongo import MongoClient

from data_models.mongo import MongoCursor
from data_models.req_body import RequestBodyItemsCreate


app = FastAPI()

db = MongoClient("mongodb://localhost:27017/")["marketplaceApi"]
db_items = db["items"]


@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


@app.get("/items")
def get_items():
    return MongoCursor(
        records=db_items.find()
    ).records


@app.post("/create_items")
def create_items(req_body: RequestBodyItemsCreate):

    response = db_items.insert_many(
        x.model_dump(exclude_none=True) for x in req_body.items
    )
    return (str(x) for x in response.inserted_ids)


@app.get("/categories")
def get_categories():
    return []