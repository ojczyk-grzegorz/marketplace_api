from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, items, auth, transactions
from app.utils.logger import get_logger
from app.utils.configs import get_settings
from app.utils.middleware import custom_middleware_factory
from app.utils.request import get_req_id


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
app.include_router(users.router)
app.include_router(items.router)
app.include_router(transactions.router)

settings = get_settings()
logger = get_logger()


@app.get("/", description="API home page.", response_class=JSONResponse)
async def home(
    req_id: Annotated[str, Depends(get_req_id)],
):
    logger.info("Test log message")
    logger.info({"message": "Home endpoint accessed", "req_id": req_id})

    return JSONResponse(
        status_code=200, content={"message": f"Hello from {settings.app_name}!"}
    )


@app.get(
    "/healthcheck", description="API healthcheck endpoint.", response_class=JSONResponse
)
async def home():
    return JSONResponse(
        status_code=200, content={"message": f"{settings.app_name} is healthy!"}
    )
