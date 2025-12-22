from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import (
    ExcInvalidCredentials,
    ExcInvalidExpiresAt,
    ExcItemNotFound,
    ExcTransactionActiveNotFound,
    ExcTransactionsFound,
    ExcUserExists,
    ExcUserNotFound,
)


def handle_invalid_credentials(
    request: Request, excepion: ExcInvalidCredentials
) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "request_id": request.uuid4,
            "code": "INVALID_CREDENTIALS",
            "message": str(excepion),
        },
    )
    return response


def handle_user_not_found(request: Request, excepion: ExcUserNotFound) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "request_id": request.uuid4,
            "code": "USER_NOT_FOUND",
            "message": str(excepion),
            "details": {
                "user_id": excepion.user_id,
            },
        },
    )
    return response


def handler_user_exists(request: Request, excepion: ExcUserExists) -> JSONResponse:
    details = {}
    if excepion.email:
        details["email"] = excepion.email
    if excepion.phone:
        details["phone"] = excepion.phone
    content = {
        "code": "USER_EXISTS",
        "message": str(excepion),
        "details": details,
    }

    response = JSONResponse(status_code=status.HTTP_409_CONFLICT, content=content)
    return response


def handle_transactions_found(
    request: Request, excepion: ExcTransactionsFound
) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "request_id": request.uuid4,
            "code": "TRANSACTIONS_FOUND",
            "message": str(excepion),
            "details": excepion.details,
        },
    )
    return response


def handle_transaction_active_not_found(
    request: Request, excepion: ExcTransactionActiveNotFound
) -> JSONResponse:
    content = {
        "code": "TRANSACTION_NOT_FOUND",
        "message": str(excepion),
    }

    details = {
        "transaction_id": excepion.transaction_id,
        "user_id_uuid4": excepion.user_id_uuid4,
    }
    content["details"] = details

    response = JSONResponse(
        status_code=404,
        content=content,
    )
    return response


def handle_item_not_found(request: Request, excepion: ExcItemNotFound) -> JSONResponse:
    content = {
        "code": "ITEM_NOT_FOUND",
        "message": str(excepion),
    }

    details = {"item_id": excepion.item_id}
    if excepion.user_id is not None:
        details["user_id"] = excepion.user_id
    if excepion.not_user_id is not None:
        details["not_user_id"] = excepion.not_user_id
    content["details"] = details

    response = JSONResponse(
        status_code=404,
        content=content,
    )
    return response


def handle_invalid_expires_at(
    request: Request, excepion: ExcInvalidExpiresAt
) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "request_id": request.uuid4,
            "code": "INVALID_EXPIRES_AT",
            "message": str(excepion),
            "details": {
                "expires_at": excepion.expires_at.isoformat(),
                "current_time": excepion.current_time.isoformat(),
            },
        },
    )
    return response


def handle_http_exception(request: Request, excepion: HTTPException) -> JSONResponse:
    response = JSONResponse(
        status_code=excepion.status_code,
        content={"request_id": request.uuid4, "code": excepion.detail},
    )
    return response


def handle_exception(request: Request, excepion: Exception) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "request_id": request.uuid4,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )
    return response


EXCEPTION_HANDLERS = {
    ExcInvalidCredentials: handle_invalid_credentials,
    ExcUserNotFound: handle_user_not_found,
    ExcUserExists: handler_user_exists,
    ExcTransactionsFound: handle_transactions_found,
    ExcTransactionActiveNotFound: handle_transaction_active_not_found,
    ExcItemNotFound: handle_item_not_found,
    ExcInvalidExpiresAt: handle_invalid_expires_at,
    HTTPException: handle_http_exception,
}
