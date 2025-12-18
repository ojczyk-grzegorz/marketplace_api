from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import get_logger

logger = get_logger()


def custom_middleware_factory(app: FastAPI):
    class CustomMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            req_id = uuid4().hex
            log = {
                "type": "request",
                "method": request.method,
                "url": str(request.url),
                "req_id": req_id,
            }
            logger.info(log)

            request.state.req_id = req_id
            response = await call_next(request)
            return response

    return CustomMiddleware(app)
