from collections.abc import Callable
from typing import Annotated
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import datetime as dt

from fastapi import FastAPI, Depends, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import users, items, auth, transactions
from app.utils.scheduler import lifespan
from app.utils.configs import get_settings, Settings
from app.constants.constants import FILENAME_LOGS

# app = FastAPI(lifespan=lifespan, tags=["Main"])
app = FastAPI(tags=["Main"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(transactions.router)

settings = get_settings()

logger = logging.getLogger(settings.logger_name)
logger.setLevel(settings.logger_level)
handler_file = TimedRotatingFileHandler(
    FILENAME_LOGS, when="M", interval=5, utc=True, encoding="utf-8"
)
formatter_file = logging.Formatter(
    fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", %(message)s}',
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler_file.setFormatter(formatter_file)
logger.addHandler(handler_file)


def custom_middleware_factory(app: FastAPI):
    class CustomMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.req_id = "1"
            response = await call_next(request)
            response.headers["X-Custom-Header"] = "CustomValue"
            return response

    return CustomMiddleware(app)


app.add_middleware(custom_middleware_factory)


def get_req_id(request: Request) -> str:
    return request.state.req_id


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        return super().default(obj)


def write_log(logger_method: Callable, message: dict):
    message = json.dumps(message, cls=CustomJSONEncoder)
    logger_method(message[1:-1])


@app.get("/", description="API home page.", response_class=JSONResponse)
async def home(
    req_id: Annotated[str, Depends(get_req_id)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    write_log(logger.info, {"message": "Home endpoint accessed", "req_id": req_id})
    return JSONResponse(
        status_code=200, content={"message": f"Hello from {settings.app_name}!"}
    )


@app.get(
    "/healthcheck", description="API healthcheck endpoint.", response_class=JSONResponse
)
async def home(
    settings: Annotated[Settings, Depends(get_settings)],
):
    return JSONResponse(
        status_code=200, content={"message": f"{settings.app_name} is healthy!"}
    )
