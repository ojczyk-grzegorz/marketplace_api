from fastapi import FastAPI

from app.routers import auth, items, transactions, user
from app.utils.configs import Settings, get_settings
from app.utils.scheduler import lifespan

app = FastAPI(lifespan=lifespan, tags=["Main"])

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(items.router)
app.include_router(transactions.router)


@app.get(
    "/",
    description="Home page of the API",
)
async def root():
    settings: Settings = get_settings()
    return {"message": f"Hello from {settings.app_name}!"}
