from pydantic import BaseModel


class ResponseSuccess(BaseModel):
    message: str
    details: dict | None = None
