import datetime as dt

from fastapi import APIRouter, Path, Body, status

from db.db import database
from datamodels.user import UserCreate, UserDB, UserPatch, UserOut, Address
from datamodels.response import ErrorResponse
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
