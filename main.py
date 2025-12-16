from typing import Annotated
import logging
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI, Depends
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
logging.basicConfig(
    level=settings.logger_level,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "log": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        TimedRotatingFileHandler(
            FILENAME_LOGS,
            when="M",
            interval=5,
            utc=True,
        ),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(settings.logger_name)


@app.get(
    "/",
    description="API home page.",
    response_class=JSONResponse
)
async def home(settings: Annotated[Settings, Depends(get_settings)]):
    logger.info("Home endpoint accessed")
    return JSONResponse(
        status_code=200,
        content={"message": f"Hello from {settings.app_name}!"}
    )


@app.get(
    "/healthcheck",
    description="API healthcheck endpoint.",
    response_class=JSONResponse
)
async def home(settings: Annotated[Settings, Depends(get_settings)],):
    return JSONResponse(
        status_code=200,
        content={"message": f"{settings.app_name} is healthy!"}
    )
