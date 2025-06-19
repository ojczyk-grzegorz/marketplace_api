from typing import Annotated

from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field

from db.db import database

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
)
async def get_user(
    user_id: int = Path(
        ...,
    ),
):
    customer_errors = []
    customer = None

    for user in database["users"]:
        if user.get("cid") == user_id:
            customer = user
            break

    if not customer:
        customer_errors.append("Customer not found")

    return dict(
        customer=customer,
        customer_errors=customer_errors,
    )


@router.post("", description="Route for creating user")
async def create_customers(
    user: dict = Body(
        ...,
        openapi_examples={
            "good": {
                "value": {
                    "email": "jakub15.nowak@example.com",
                    "phone": "+48634489566",
                    "first_name": "Jakub",
                    "last_name": "Nowak",
                    "birth_date": "1998-11-21",
                    "country": "Poland",
                    "city": "Ruda \u015al\u0105ska",
                    "street": "W\u0142oska",
                    "street_number": 38,
                    "postal_code": "49-201",
                    "created_at": "2025-01-06T00:00:00",
                    "rating": 4.0,
                }
            },
            "bad": {
                "value": {
                    "email": "jakub.nowak@example.com",
                    "phone": "+48634489566",
                    "first_name": "Jakub",
                    "last_name": "Nowak",
                    "birth_date": "1998-11-21",
                    "country": "Poland",
                    "city": "Ruda \u015al\u0105ska",
                    "street": "W\u0142oska",
                    "street_number": 38,
                    "postal_code": "49-201",
                    "created_at": "2025-01-06T00:00:00",
                    "rating": 4.0,
                }
            },
        },
    ),
):
    user_errors = []

    db_users = database["users"]
    email = user.get("email")
    for du in db_users:
        if du.get("email") == email:
            user_errors.append(
                {
                    "error": "User with this email already exists",
                    "email": email,
                }
            )
            user = None
            break
    else:
        user_id = max([x["cid"] for x in db_users], default=0) + 1
        user["cid"] = user_id

    return dict(
        user=user,
        user_errors=user_errors,
    )


@router.patch("")
async def update_customers(
    users: list[dict] = Body(
        ...,
        min_length=1,
        max_length=20,
        openapi_examples={
            "good": {
                "value": [
                    {
                        "cid": 0,
                        "email": "jakub22.nowak@example.com",
                        "phone": "+48634489566",
                        "first_name": "Jakub",
                        "last_name": "Nowak",
                        "birth_date": "1998-11-21",
                        "country": "Poland",
                        "city": "Ruda \u015al\u0105ska",
                        "street": "W\u0142oska",
                        "street_number": 38,
                        "postal_code": "49-201",
                        "created_at": "2025-01-06T00:00:00",
                        "rating": 4.0,
                    }
                ]
            },
            "bad": {
                "value": [
                    {
                        "cid": 10_000_000,
                        "email": "jakub23.nowak@example.com",
                        "phone": "+48634489566",
                        "first_name": "Jakub",
                        "last_name": "Nowak",
                        "birth_date": "1998-11-21",
                        "country": "Poland",
                        "city": "Ruda \u015al\u0105ska",
                        "street": "W\u0142oska",
                        "street_number": 38,
                        "postal_code": "49-201",
                        "created_at": "2025-01-06T00:00:00",
                        "rating": 4.0,
                    }
                ]
            },
        },
    ),
):
    users_updated = []
    users_errors = []

    db_users = database["users"]
    for user in users:
        for du in db_users:
            if du.get("cid") == user.get("cid"):
                du.update(user)
                users_updated.append(du)
                break
        else:
            users_errors.append(
                {
                    "error": "User not found",
                    "user": user,
                }
            )

    return dict(users_updated=users_updated, users_errors=users_errors)
