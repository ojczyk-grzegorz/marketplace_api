from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    details: dict | str | None = None
