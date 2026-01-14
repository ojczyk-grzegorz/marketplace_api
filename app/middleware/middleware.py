from collections.abc import Callable
import datetime as dt
from uuid import uuid4

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.logger.utils import get_logger, log_error

logger = get_logger()


class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        req_id = uuid4()
        log = {
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            "req_id": req_id,
            "type": "request",
            "method": request.method,
            "url": str(request.url),
        }
        logger.info(log)

        request.state.req_id = req_id
        try:
            response = await call_next(request)
        except Exception as e:
            log_error(logger, req_id, e)
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error"},
            )
        response.headers["X-Request-ID"] = str(req_id)
        log = {
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            "req_id": req_id,
            "type": "response",
            "status_code": response.status_code,
        }
        logger.info(log)
        return response
