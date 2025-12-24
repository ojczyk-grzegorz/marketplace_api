from pydantic import BaseModel


class ResponseGetToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
