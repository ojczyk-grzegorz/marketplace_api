import uvicorn

from fastapi import FastAPI

from routers import users, items, auth, transactions
from utils.scheduler import lifespan
from utils.logs import logger


app = FastAPI(lifespan=lifespan, tags=["Main"])

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(transactions.router)


@app.get(
    "/",
    description="Health check",
)
async def root():
    return {"message": "Application is up and running"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="trace")
