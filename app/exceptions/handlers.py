from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError
from pydantic import BaseModel

from app.exceptions.exceptions import (
    ExcDiscountActiveNotFound,
    ExcInsufficientStock,
    ExcInvalidCredentials,
    ExcItemNotFound,
    ExcTransactionActiveNotFound,
    ExcTransactionFinalizedNotFound,
    ExcTransactionsActiveFound,
    ExcUserExists,
    ExcUserNotFound,
    ExcDeliveryOptionNotFound
)
from app.logger.utils import get_logger

logger = get_logger()


class ExceptionResponseModel(BaseModel):
    error_code: str
    message: str
    details: dict | None = None


def log_error(request: Request, exc: HTTPException):
    logger.error(
        {
            "type": "http_exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "req_id": getattr(request.state, "req_id", None),
        }
    )


async def exception_handler_validation_error(request, exc: RequestValidationError):
    logger.error(
        {
            "type": "validation_exception",
            "detail": exc.errors(),
            "body": exc.body,
            "req_id": getattr(request.state, "req_id", None),
        }
    )
    return JSONResponse(
        status_code=422,
        content=dict(
            error_code="VALIDATION_ERROR",
            message="Input validation failed.",
        ),
    )


async def exception_handler_http(request, exc: HTTPException):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="ERROR",
            message=exc.detail,
        ),
    )


async def exception_handler_user_exists(request, exc: ExcUserExists):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="USER_EXISTS",
            message=exc.detail,
            details={
                "email": exc.email,
                "phone": exc.phone,
            },
        ),
    )


async def exception_handler_transaction_active_not_found(
    request, exc: ExcTransactionActiveNotFound
):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="TRANSACTION_ACTIVE_NOT_FOUND",
            message=exc.detail,
            details={
                "transaction_id": str(exc.transaction_id),
                "user_id": str(exc.user_id),
            },
        ),
    )

async def exception_handler_delivery_option_not_found(
    request, exc: ExcDeliveryOptionNotFound
):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="DELIVERY_OPTION_NOT_FOUND",
            message=exc.detail,
            details={
                "delivery_option_id": str(exc.delivery_option_id),
            },
        ),
    )


async def exception_handler_transaction_finalized_not_found(
    request, exc: ExcTransactionFinalizedNotFound
):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="TRANSACTION_FINALIZED_NOT_FOUND",
            message=exc.detail,
            details={
                "transaction_id": str(exc.transaction_id),
                "user_id": str(exc.user_id),
            },
        ),
    )


async def exception_handler_transactions_active_found(request, exc: ExcTransactionsActiveFound):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="TRANSACTIONS_ACTIVE_FOUND",
            message=exc.detail,
            details={
                "user_id": str(exc.user_id),
                "transaction_ids": [str(tid) for tid in exc.transaction_ids],
            },
        ),
    )


async def exception_handler_item_not_found(request, exc: ExcItemNotFound):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="ITEM_NOT_FOUND",
            message=exc.detail,
            details={
                "item_id": str(exc.item_id),
            },
        ),
    )


async def exception_handler_invalid_credentials(request, exc: ExcInvalidCredentials):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="INVALID_CREDENTIALS",
            message=exc.detail,
        ),
    )


async def exception_handler_user_not_found(request, exc: ExcUserNotFound):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="USER_NOT_FOUND",
            message=exc.detail,
            details={
                "user_id": str(exc.user_id),
            },
        ),
    )


async def exception_handler_token_expired(request, exc: ExpiredSignatureError):
    logger.error(
        {
            "type": "token_expired_exception",
            "detail": str(exc),
            "req_id": getattr(request.state, "req_id", None),
        }
    )
    return JSONResponse(
        status_code=401,
        content=dict(
            error_code="TOKEN_EXPIRED",
            message="The provided token has expired.",
        ),
    )


async def exception_handler_discount_active_not_found(request, exc: ExcDiscountActiveNotFound):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="DISCOUNT_ACTIVE_NOT_FOUND",
            message=exc.detail,
            details={
                "discount_code": str(exc.discount_code),
            },
        ),
    )


async def exception_handler_insufficient_stock(request, exc: ExcInsufficientStock):
    log_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="INSUFFICIENT_STOCK",
            message=exc.detail,
            details={
                "item_id": str(exc.item_id),
                "requested": exc.requested,
                "available": exc.available,
            },
        ),
    )


EXCEPTION_HANDLERS = {
    HTTPException: exception_handler_http,
    RequestValidationError: exception_handler_validation_error,
    ExcUserExists: exception_handler_user_exists,
    ExcTransactionActiveNotFound: exception_handler_transaction_active_not_found,
    ExcDeliveryOptionNotFound: exception_handler_delivery_option_not_found,
    ExcTransactionsActiveFound: exception_handler_transactions_active_found,
    ExcTransactionFinalizedNotFound: exception_handler_transaction_finalized_not_found,
    ExcItemNotFound: exception_handler_item_not_found,
    ExcInvalidCredentials: exception_handler_invalid_credentials,
    ExcUserNotFound: exception_handler_user_not_found,
    ExpiredSignatureError: exception_handler_token_expired,
    ExcDiscountActiveNotFound: exception_handler_discount_active_not_found,
    ExcInsufficientStock: exception_handler_insufficient_stock,
}
