from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware


def custom_middleware_factory(app: FastAPI):
    class CustomMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.req_id = "1"
            response = await call_next(request)
            return response

    return CustomMiddleware(app)
