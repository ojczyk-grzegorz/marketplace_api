from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import users, items, transactions, auth


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(transactions.router)


@app.get(
    "/",
    description="Health check",
)
async def root():
    return {"message": "Application is up and running"}
