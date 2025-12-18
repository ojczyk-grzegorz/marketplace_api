from fastapi import FastAPI

from app.routers import user, items, auth, transactions
from app.utils.scheduler import lifespan
from app.utils.configs import get_settings, Settings

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
