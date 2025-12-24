from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger.utils import get_logger

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
            try:
                response = await call_next(request)
            except Exception as e:
                log = {
                    "type": "error",
                    "message": str(e),
                    "req_id": req_id,
                }
                logger.error(log)
                raise e from e
                response = JSONResponse(
                    status_code=500,
                    content={"error": "Internal Server Error"},
                )
            response.headers["X-Request-ID"] = req_id
            return response

    return CustomMiddleware(app)
