import datetime as dt
from pydantic import BaseModel, ConfigDict
from typing import Optional


class User(BaseModel):
    model_config=ConfigDict(extra="ignore")
    
    _id: str | None = None

    created_at: dt.datetime = dt.datetime.now(dt.UTC)
    updated_at: dt.datetime = dt.datetime.now(dt.UTC)
    username: str
    email: str
    password_hash: str
    is_active: bool = True
    is_admin: bool = False