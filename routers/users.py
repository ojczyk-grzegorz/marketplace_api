import datetime as dt

from fastapi import APIRouter, Path, Body, status, Header

from db.db import database
from datamodels.user import UserCreate, UserDB, UserPatch, UserOut, Address
from datamodels.response import ErrorResponse
from auth.auth import get_access_token, validate_access_token, KEY, ALGORITHM
from testing.openapi.users import USER_CREATE, USER_PATCH


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user(
    user_id: int = Path(
        ...,
    ),
):
    for user in database["users"]:
        if user.get("uid") == user_id:
            reviews = user.get("reviews", [])
            if len(reviews) > 3:
                user["reviews"] = reviews[len(reviews) - 3 :]
                return user

    return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=dict | ErrorResponse,
    description="Route for getting user by ID",
)
async def login(
    req_body: dict = Body(
        ...,
        openapi_examples={
            "example1": {
                "summary": "Login with email and password",
                "value": {"email": "jakub.nowak@example.com", "password": "password"},
            }
        },
    ),
):
    users_db = database["users"]

    email = req_body["email"]
    password = req_body["password"]

    password_hash = password + "_hash"

    for user in users_db:
        if user.get("email") == email and user.get("password_hash") == password_hash:
            token = get_access_token(
                data={"user_id": user["uid"]},
                secret_key=KEY,
                algorithm=ALGORITHM,
                expire_minutes=60,
            )

            return dict(
                access_token=token,
                token_type="bearer",
                user_id=user["uid"],
            )

    return ErrorResponse(
        error="INVALID_CREDENTIALS",
    )


@router.get(
    "/me/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDB | ErrorResponse,
    description="Route for getting user by ID",
)
async def get_user_me(
    user_id: int = Path(
        ...,
    ),
    authorization: str = Header(..., alias="Authorization"),
):
    validate_access_token(
        token=authorization,
        secret_key=KEY,
        algorithms=[ALGORITHM],
        user_id=user_id,
    )
    for user in database["users"]:
        if user.get("uid") == user_id:
            reviews = user.get("reviews", [])
            if len(reviews) > 3:
                user["reviews"] = reviews[len(reviews) - 3 :]
            break

    else:
        return ErrorResponse(error="USER_NOT_FOUND", details={"user_id": user_id})

    return user


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for creating user",
)
async def create_customers(
    user: UserCreate = Body(..., openapi_examples=USER_CREATE),
):
    db_users = database["users"]
    for du in db_users:
        if du.get("email") == user.email:
            return ErrorResponse(
                error="USER_ALREADY_EXISTS", details={"email": user.email}
            )
    else:
        user_id = max([x["uid"] for x in db_users], default=0) + 1
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()

        user = UserDB(
            **user.model_dump(exclude_none=True, exclude_unset=True),
            uid=user_id,
            created_at=created_at,
            updated_at=created_at,
            addresses=[
                Address(
                    type="home",
                    **user.model_dump(exclude_none=True, exclude_unset=True),
                )
            ],
            reviews=[],
            rating=0.0,
            avatar=None,
            last_activity=created_at,
        )

        db_users.append(user.model_dump())

    return user


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserOut | ErrorResponse,
    description="Route for creating user",
)
async def update_customers(
    user: UserPatch = Body(
        ...,
        openapi_examples=USER_PATCH,
    ),
):
    db_users: list[dict] = database["users"]
    for du in db_users:
        if du.get("uid") == user.uid:
            du.update(user.model_dump(exclude_none=True, exclude_unset=True))
            reviews = du.get("reviews", [])
            if len(reviews) > 3:
                du["reviews"] = reviews[len(reviews) - 3 :]
            return du

    return ErrorResponse(error="USER_NOT_FOUND", details={"uid": user.uid})
