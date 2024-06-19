from pydantic import BaseModel

from data_models.item import Item
from data_models.user import User


class RequestBodyItemsCreate(BaseModel):
    items: list[Item]

class RequestBodyUsersCreate(BaseModel):
    users: list[User]