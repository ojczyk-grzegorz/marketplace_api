import datetime as dt

from pydantic import BaseModel, field_validator


class LogRequest(BaseModel):
    rid_uuid4: str
    timestamp: dt.datetime
    url: str
    method: str
    status_code: int
    duration_ms: float
    type: str
    http_version: str
    server: list | None = None
    client: list | None = None
    path: str
    path_params: dict | None = None
    asgi_version: str
    asgi_spec_version: str
    request_headers: dict | None = None
    request_body: dict | None = None
    response_headers: dict | None = None
    response_body: dict | None = None
    exception: dict | None = None

    @field_validator("*", mode="before")
    def validate_fields(cls, value):
        if value == "":
            return None
        return value
