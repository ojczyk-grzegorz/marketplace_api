from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    details: dict | None = None
