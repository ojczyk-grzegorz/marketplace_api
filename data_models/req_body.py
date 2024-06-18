from pydantic import BaseModel

from data_models.item import Item


class RequestBodyItemsCreate(BaseModel):
    items: list[Item]