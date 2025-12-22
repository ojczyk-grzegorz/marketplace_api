from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, text

from app.routers import auth, items, transactions, user
from app.utils.configs import get_settings
from app.utils.db import get_db_session
from app.utils.logger import get_logger
from app.utils.middleware import custom_middleware_factory

app = FastAPI(tags=["Main"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(custom_middleware_factory)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(items.router)
app.include_router(transactions.router)

settings = get_settings()
logger = get_logger()


@app.get("/", description="API home page.", response_class=JSONResponse)
async def home():
    return JSONResponse(
        status_code=200, content={"message": f"Hello from {settings.app_name}!"}
    )


@app.get(
    "/healthcheck", description="API healthcheck endpoint.", response_class=JSONResponse
)
async def healthcheck(db: Annotated[Session, Depends(get_db_session)]):
    db.exec(text("SELECT 1 as test")).fetchone()
    return JSONResponse(
        status_code=200, content={"message": f"{settings.app_name} is healthy!"}
    )
