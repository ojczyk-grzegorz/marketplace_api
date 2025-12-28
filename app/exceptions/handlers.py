from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError
from pydantic import BaseModel

from app.exceptions.exceptions import (
    ExcDeliveryOptionNotFound,
    ExcDiscountActiveNotFound,
    ExcInsufficientStock,
    ExcInvalidCredentials,
    ExcItemNotFound,
    ExcTransactionActiveNotFound,
    ExcTransactionFinalizedNotFound,
    ExcTransactionsActiveFound,
    ExcUserExists,
    ExcUserNotFound,
)
from app.logger.utils import get_logger, log_error

logger = get_logger()


class ExceptionResponseModel(BaseModel):
    error_code: str
    message: str
    details: dict | None = None



async def exception_handler_validation_error(request: Request, exc: RequestValidationError):
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=422,
        content=dict(
            error_code="VALIDATION_ERROR",
            message="Input validation failed.",
        ),
    )


async def exception_handler_http(request: Request, exc: HTTPException):
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="ERROR",
            message=exc.detail,
        ),
    )


async def exception_handler_user_exists(request: Request, exc: ExcUserExists):
    log_error(logger, request.state.req_id, exc)
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
    request: Request, exc: ExcTransactionActiveNotFound
):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_delivery_option_not_found(request: Request, exc: ExcDeliveryOptionNotFound):
    log_error(logger, request.state.req_id, exc)
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
    request: Request, exc: ExcTransactionFinalizedNotFound
):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_transactions_active_found(request: Request, exc: ExcTransactionsActiveFound):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_item_not_found(request: Request, exc: ExcItemNotFound):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_invalid_credentials(request: Request, exc: ExcInvalidCredentials):
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="INVALID_CREDENTIALS",
            message=exc.detail,
        ),
    )


async def exception_handler_user_not_found(request: Request, exc: ExcUserNotFound):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_token_expired(request: Request, exc: ExpiredSignatureError):
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=401,
        content=dict(
            error_code="TOKEN_EXPIRED",
            message="The provided token has expired.",
        ),
    )


async def exception_handler_discount_active_not_found(request: Request, exc: ExcDiscountActiveNotFound):
    log_error(logger, request.state.req_id, exc)
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


async def exception_handler_insufficient_stock(request: Request, exc: ExcInsufficientStock):
    log_error(logger, request.state.req_id, exc)
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
