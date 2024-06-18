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


class ItemPrice(BaseModel):
    model_config=ConfigDict(extra="allow")
    
    currency: str
    base_100: int
    tax_100: int

class ItemFeatures(BaseModel):
    model_config=ConfigDict(extra="allow")


class ItemPost(BaseModel):
    model_config=ConfigDict(extra="allow")

    description: str | None = None
    post: str | None = None

class Item(BaseModel):
    _id: str | None = None
    name: str
    price: ItemPrice
    post: ItemPost
    features: ItemFeatures
    categories: list[str]
    subcategories: list[str]

class RequestItemsCreate(BaseModel):
    items: list[Item]


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
def create_items(items: list[Item]):

    response = db_items.insert_many(
        x.model_dump(exclude_none=True) for x in items
    )
    return (str(x) for x in response.inserted_ids)


@app.get("/categories")
def get_categories():
    return []