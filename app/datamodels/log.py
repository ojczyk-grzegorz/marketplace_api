from pydantic import BaseModel, field_validator
import datetime as dt


class LogRequest(BaseModel):
    rid_uuid4: str | None = None
    timestamp: dt.datetime | None = None
    url: str | None = None
    method: str | None = None
    status_code: int | None = None
    duration_ms: float | None = None
    type: str | None = None
    http_version: str | None = None
    server: list | None = None
    client: list | None = None
    path: str | None = None
    path_params: dict | None = None
    asgi_version: str | None = None
    asgi_spec_version: str | None = None
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
