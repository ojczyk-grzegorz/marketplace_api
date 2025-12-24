import uuid
from pydantic import BaseModel, EmailStr, Field


class UserToCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str = Field(..., exclude=True)


class UserToUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = Field(None, exclude=True)


class UserCreated(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    phone: str


class UserUpdated(UserCreated):
    user_id: uuid.UUID
    email: EmailStr | None = None
    phone: str | None = None
    password_changed: bool = False


class UserRemoved(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    phone: str


class ResponseCreateUser(BaseModel):
    user_created: UserCreated


class ResponseUpdateUser(BaseModel):
    user_updated: UserUpdated


class ResponseRemoveUser(BaseModel):
    user_removed: UserRemoved
