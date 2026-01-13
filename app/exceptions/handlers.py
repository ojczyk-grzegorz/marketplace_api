from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.exceptions.exceptions import (
    ExcDeliveryOptionNotFound,
    ExcDiscountActiveNotFound,
    ExcExpiredToken,
    ExcInsufficientStock,
    ExcInvalidCredentials,
    ExcInvalidToken,
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


async def exception_handler_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=422,
        content=dict(
            error_code="VALIDATION_ERROR",
            message="Input validation failed.",
        ),
    )


async def exception_handler_http(request: Request, exc: HTTPException) -> JSONResponse:
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="ERROR",
            message=exc.detail,
        ),
    )


async def exception_handler_user_exists(request: Request, exc: ExcUserExists) -> JSONResponse:
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
) -> JSONResponse:
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


async def exception_handler_delivery_option_not_found(
    request: Request, exc: ExcDeliveryOptionNotFound
) -> JSONResponse:
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
) -> JSONResponse:
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


async def exception_handler_transactions_active_found(
    request: Request, exc: ExcTransactionsActiveFound
) -> JSONResponse:
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


async def exception_handler_item_not_found(request: Request, exc: ExcItemNotFound) -> JSONResponse:
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


async def exception_handler_invalid_credentials(
    request: Request, exc: ExcInvalidCredentials
) -> JSONResponse:
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="INVALID_CREDENTIALS",
            message=exc.detail,
        ),
    )


async def exception_handler_user_not_found(request: Request, exc: ExcUserNotFound) -> JSONResponse:
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


async def exception_handler_discount_active_not_found(
    request: Request, exc: ExcDiscountActiveNotFound
) -> JSONResponse:
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


async def exception_handler_insufficient_stock(
    request: Request, exc: ExcInsufficientStock
) -> JSONResponse:
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


async def exception_handler_invalid_token(request: Request, exc: ExcInvalidToken) -> JSONResponse:
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="INVALID_TOKEN",
            message=exc.detail,
        ),
    )


async def exception_handler_token_expired(request: Request, exc: ExcExpiredToken) -> JSONResponse:
    log_error(logger, request.state.req_id, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            error_code="TOKEN_EXPIRED",
            message=exc.detail,
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
    ExcDiscountActiveNotFound: exception_handler_discount_active_not_found,
    ExcInsufficientStock: exception_handler_insufficient_stock,
    ExcInvalidToken: exception_handler_invalid_token,
    ExcExpiredToken: exception_handler_token_expired,
}
