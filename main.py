from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import users, items, auth, transactions
from exceptions.exceptions import ExcUserNotFound, ExcUserExists, ExcTransactionsFound, ExcItemNotFound, ExcInvalidExpiresAt


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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


@app.exception_handler(ExcUserNotFound)
async def handle_user_not_found(request: Request, exc: ExcUserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "code": "USER_NOT_FOUND",
            "message": str(exc),
            "details": {
                "user_id": exc.user_id,
            },
        },
    )


@app.exception_handler(ExcUserExists)
async def handle_user_not_found(request: Request, exc: ExcUserExists):
    details = {}
    if exc.email:
        details["email"] = exc.email
    if exc.phone:
        details["phone"] = exc.phone
    content = {"code": "USER_EXISTS", "message": str(exc), "details": details}

    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=content)


@app.exception_handler(ExcTransactionsFound)
async def handle_transactions_found(request: Request, exc: ExcTransactionsFound):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "code": "TRANSACTIONS_FOUND",
            "message": str(exc),
            "details": exc.details,
        },
    )


@app.exception_handler(ExcItemNotFound)
async def handle_user_not_found(request: Request, exc: ExcItemNotFound):
    content={
        "code": "ITEM_NOT_FOUND",
        "message": str(exc),
    }

    details = {"item_id": exc.item_id}
    if exc.user_id is not None:
        details["user_id"] = exc.user_id
    if exc.not_user_id is not None:
        details["not_user_id"] = exc.not_user_id
    content["details"] = details

    return JSONResponse(
        status_code=404,
        content=content,
    )


@app.exception_handler(ExcInvalidExpiresAt)
async def handle_invalid_expires_at(request: Request, exc: ExcInvalidExpiresAt):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": "INVALID_EXPIRES_AT",
            "message": str(exc),
            "details": {
                "expires_at": exc.expires_at.isoformat(),
                "current_time": exc.current_time.isoformat(),
            },
        },
    )