from uuid import uuid4
import time
import os
import datetime as dt
from typing import Callable
import json
import traceback

from fastapi import Request, Response
from fastapi.routing import APIRoute

from app.datamodels.log import LogRequest
from app.constants.constants import DIR_LOGS_REQUEST

from app.exceptions.handlers import EXCEPTION_HANDLERS, handle_exception


def custom_serializer(obj):
    if isinstance(obj, bytes):
        obj = obj.decode("utf-8")
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            return obj
    else:
        return str(obj)


def redact_headers(headers: dict) -> dict:
    redacted_headers = {}
    for key, value in headers.items():
        if key.lower() in ["authorization", "cookie"]:
            redacted_headers[key] = "<redacted>"
        else:
            redacted_headers[key] = value
    return redacted_headers


def redact_request_body(body: bytes) -> dict:
    try:
        body = body.decode("utf-8")
        return json.loads(body)
    except json.JSONDecodeError:
        if body.startswith("grant_type=password"):
            return {"request_body": "<redacted>"}
        return body


def redact_response_body(body: bytes) -> dict:
    try:
        body = body.decode("utf-8")
        response_body = json.loads(body)
        if isinstance(response_body, dict) and "access_token" in response_body:
            response_body["access_token"] = "<redacted>"
        return response_body
    except json.JSONDecodeError:
        return body.decode("utf-8")


def get_log_request(
    request_headers: dict,
    request: Request,
    request_body: dict,
    response: Response,
    response_headers: dict,
    response_body: dict,
    duration_ms: float,
    exception: Exception = None,
) -> LogRequest:
    trcb = []
    if exception:
        for obj in traceback.format_exception(
            # !!!!!!!
            type(exception),
            exception,
            exception.__traceback__,
        ):
            obj: str
            lines = obj.split("\n")
            for line in lines:
                trcb.append(line)

    log_request = LogRequest(
        rid_uuid4=request.uuid4,
        timestamp=request.timestamp,
        url=str(request.url),
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
        type=request.scope.get("type"),
        http_version=request.scope.get("http_version"),
        server=request.scope.get("server"),
        client=request.scope.get("client"),
        path=request.scope.get("path"),
        path_params=request.path_params,
        asgi_version=request.scope.get("asgi", {}).get("version"),
        asgi_spec_version=request.scope.get("asgi", {}).get("spec_version"),
        request_headers=request_headers,
        request_body=request_body,
        response_headers=response_headers,
        response_body=response_body,
        exception=(
            None
            if not exception
            else dict(
                type=type(exception).__name__,
                message=str(exception),
                args=exception.log_args if hasattr(exception, "log_args") else {},
                traceback=trcb,
            )
        ),
    )

    return log_request


def save_log_request(log_request: LogRequest) -> None:
    os.makedirs(DIR_LOGS_REQUEST, exist_ok=True)

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
    with open(os.path.join(DIR_LOGS_REQUEST, timestamp + ".log"), "a") as log_file:
        log_file.write("\n" + log_request.model_dump_json())


class APIRouteLogging(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_uuid4 = uuid4().hex
            timestamp = dt.datetime.now(dt.timezone.utc)

            request.uuid4 = request_uuid4
            request.timestamp = timestamp

            request_body = await request.body()
            start = time.perf_counter_ns()

            exception = None
            try:
                response: Response = await original_route_handler(request)
            except Exception as exc:
                exception = exc
                handler = EXCEPTION_HANDLERS.get(type(exc), handle_exception)
                response = handler(request, exception)

            duration_ms = round((time.perf_counter_ns() - start) / 1_000_000, 2)

            request_headers = redact_headers(dict(request.headers))
            request_body = (
                redact_request_body(request_body)
                if isinstance(request_body, bytes)
                else request_body
            )
            response_headers = dict(response.headers)
            response_body = (
                redact_response_body(response.body)
                if isinstance(response.body, bytes)
                else response.body
            )

            log_request = get_log_request(
                request_headers=request_headers,
                request=request,
                request_body=request_body,
                response=response,
                response_headers=response_headers,
                response_body=response_body,
                duration_ms=duration_ms,
                exception=exception,
            )
            save_log_request(log_request)

            return response

        return custom_route_handler
