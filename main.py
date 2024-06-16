import bson.json_util
from fastapi import FastAPI
from pymongo import MongoClient
import bson
from pydantic import BaseModel, ConfigDict, field_serializer, Field
from decimal import Decimal


class MongoDocument(BaseModel):
    model_config=ConfigDict(extra="allow", arbitrary_types_allowed=True)
    id: bson.ObjectId | str = Field(alias="_id")

    @field_serializer("id")
    def id_serialize(self, value: bson.ObjectId) -> str:
        return str(value)

class MongoCursor(BaseModel):
    records: list[MongoDocument]

class Item(BaseModel):
    name: str
    price: Decimal
    currency: str
    categories: list[str]
    subcategories: list[str]
    description: str | None = None
    post: str | None = None


app = FastAPI()
db = MongoClient("mongodb://localhost:27017/")["marketplaceApi"]

@app.get("/", description="Home page")
def home():
    return {"message": "Welcome to my marketplace ;)"}


@app.get("/items")
def get_items():
    return MongoCursor(
        records=db["items"].find()
    ).records


@app.post("/create_items")
def create_items(items: list[Item]):
    response = db["items"].insert_many([item.model_dump() for item in items])
    return [str(x) for x in response.inserted_ids]


@app.get("/categories")
def get_categories():
    return []