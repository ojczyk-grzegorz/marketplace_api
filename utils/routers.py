from uuid import uuid4
import time
import os
import datetime as dt
from typing import Callable
import json
import traceback

from fastapi import Request, Response, status, HTTPException
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

from datamodels.log import LogRequest

from exceptions.exceptions import (
    ExcInvalidCredentials,
    ExcUserNotFound,
    ExcUserExists,
    ExcTransactionsFound,
    ExcTransactionActiveNotFound,
    ExcItemNotFound,
    ExcInvalidExpiresAt,
)


def custom_serializer(obj):
    if isinstance(obj, bytes):
        obj = obj.decode("utf-8")
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            return obj
    else:
        return str(obj)


class APIRouteLogging(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_uuid4 = uuid4().hex
            timestamp = dt.datetime.now(dt.timezone.utc).isoformat()

            request.uuid4 = request_uuid4
            request.timestamp = timestamp

            request_body = await request.body()
            start = time.perf_counter_ns()

            excepion = None
            try:
                response: Response = await original_route_handler(request)
            except ExcInvalidCredentials as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "code": "INVALID_CREDENTIALS",
                        "message": str(exc),
                    },
                )

            except ExcUserNotFound as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "code": "USER_NOT_FOUND",
                        "message": str(exc),
                        "details": {
                            "user_id": exc.user_id,
                        },
                    },
                )

            except ExcUserExists as exc:
                excepion = exc
                details = {}
                if exc.email:
                    details["email"] = exc.email
                if exc.phone:
                    details["phone"] = exc.phone
                content = {
                    "code": "USER_EXISTS",
                    "message": str(exc),
                    "details": details,
                }

                response = JSONResponse(
                    status_code=status.HTTP_409_CONFLICT, content=content
                )

            except ExcTransactionsFound as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "code": "TRANSACTIONS_FOUND",
                        "message": str(exc),
                        "details": exc.details,
                    },
                )

            except ExcTransactionActiveNotFound as exc:
                excepion = exc
                content = {
                    "code": "TRANSACTION_NOT_FOUND",
                    "message": str(exc),
                }

                details = {
                    "transaction_id": exc.transaction_id,
                    "user_id_uuid4": exc.user_id_uuid4,
                }
                content["details"] = details

                response = JSONResponse(
                    status_code=404,
                    content=content,
                )

            except ExcItemNotFound as exc:
                excepion = exc
                content = {
                    "code": "ITEM_NOT_FOUND",
                    "message": str(exc),
                }

                details = {"item_id": exc.item_id}
                if exc.user_id is not None:
                    details["user_id"] = exc.user_id
                if exc.not_user_id is not None:
                    details["not_user_id"] = exc.not_user_id
                content["details"] = details

                response = JSONResponse(
                    status_code=404,
                    content=content,
                )

            except ExcInvalidExpiresAt as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "code": "INVALID_EXPIRES_AT",
                        "message": str(exc),
                        "details": {
                            "expires_at": exc.expires_at.isoformat(),
                            "current_time": exc.current_time.isoformat(),
                        },
                    },
                )

            except HTTPException as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=exc.status_code,
                    content={"code": exc.detail},
                )

            except Exception as exc:
                excepion = exc
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                    },
                )

            duration_ms = round((time.perf_counter_ns() - start) / 1_000_000, 2)
            request_headers = dict(request.headers)
            if "authorization" in request_headers:
                request_headers["authorization"] = "<redacted>"
            if "cookie" in request_headers:
                request_headers["cookie"] = "<redacted>"

            request_body = request_body
            if isinstance(request_body, bytes):
                try:
                    request_body = json.loads(request_body.decode("utf-8"))
                except json.JSONDecodeError:
                    request_body = request_body.decode("utf-8")
                    if request_body.startswith("grant_type=password"):
                        request_body = {"request_body": "<redacted>"}
            response_headers = dict(response.headers)
            response_body = response.body
            if isinstance(response_body, bytes):
                try:
                    response_body = json.loads(response_body.decode("utf-8"))
                    if (
                        isinstance(response_body, dict)
                        and "access_token" in response_body
                    ):
                        response_body["access_token"] = "<redacted>"

                except json.JSONDecodeError:
                    response_body = response_body.decode("utf-8")

            trcb = []
            if excepion:
                for obj in traceback.format_exception(
                    type(excepion), excepion, excepion.__traceback__
                ):
                    obj: str
                    lines = obj.split("\n")
                    for line in lines:
                        trcb.append(line)

            log_data = LogRequest(
                rid_uuid4=request_uuid4,
                timestamp=timestamp,
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
                    if not excepion
                    else dict(
                        type=type(excepion).__name__,
                        message=str(excepion),
                        args=excepion.log_args if hasattr(excepion, "log_args") else {},
                        traceback=trcb,
                    )
                ),
            )

            dir_logs = "logs"
            os.makedirs(dir_logs, exist_ok=True)

            timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
            with open(os.path.join(dir_logs, timestamp + ".json"), "a") as log_file:
                log_file.write("\n" + log_data.model_dump_json())

            return response

        return custom_route_handler
