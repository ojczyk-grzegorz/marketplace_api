from collections.abc import AsyncGenerator
import contextlib
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, text

from app.configs.datamodels import Settings
from app.configs.utils import get_settings
from app.database.utils import get_db_session
from app.exceptions.handlers import EXCEPTION_HANDLERS
from app.logger.utils import get_logger
from app.middleware.middleware import CustomMiddleware
from app.routers.auth import auth
from app.routers.items import items
from app.routers.transactions import transactions
from app.routers.user import user

logger = get_logger()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up the API.")
    yield
    logger.info("Shutting down the API.")


app = FastAPI(
    title="Generic e-commerce API",
    description="A generic e-commerce API built with FastAPI and SQLModel for learning purposes.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CustomMiddleware)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(items.router)
app.include_router(transactions.router)
app.exception_handlers.update(EXCEPTION_HANDLERS)


@app.get("/", description="API home page.", response_class=JSONResponse)
async def get_home(settings: Annotated[Settings, Depends(get_settings)]) -> JSONResponse:
    return JSONResponse(status_code=200, content={"message": f"Hello from {settings.app_name}!"})


@app.get("/healthcheck", description="API healthcheck endpoint.", response_class=JSONResponse)
async def get_healthcheck(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
) -> JSONResponse:
    db.exec(text("SELECT 1 as test")).first()
    return JSONResponse(status_code=200, content={"message": f"{settings.app_name} is healthy!"})
