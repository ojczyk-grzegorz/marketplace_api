import uvicorn

from fastapi import FastAPI, Depends

from routers import users, items, auth, transactions
from utils.scheduler import lifespan
from utils.configs import get_settings, Settings

app = FastAPI(lifespan=lifespan, tags=["Main"])

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(transactions.router)


@app.get(
    "/",
    description="Home page of the API",
)
async def root(settings: Settings = Depends(get_settings)):
    return {"message": f"Hello from {settings.app_name}!"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )
