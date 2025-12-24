from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.routing import APIRoute
from sqlmodel import Session

from app.auth.utils import oauth2_scheme
from app.configs.datamodels import Settings
from app.configs.utils import get_settings
from app.database.utils import get_db_session
from app.routers.user.datamodels import (
    ResponseCreateUser,
    ResponseRemoveUser,
    ResponseUpdateUser,
    UserToCreate,
    UserToUpdate,
)
from app.routers.user.service import (
    create_user,
    remove_user,
    update_user,
)
from development.openapi_examples import (
    get_user_create_examples,
    get_user_update_examples,
)

router = APIRouter(prefix="/users", tags=["Users"], route_class=APIRoute)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    response_model_exclude_none=True,
    description="Route for creating user",
)
async def req_create_user(
    db: Annotated[Session, Depends(get_db_session)],
    user_req: Annotated[
        UserToCreate,
        Body(..., openapi_examples=get_user_create_examples()),
    ],
):
    return await create_user(db=db, user_req=user_req)


@router.patch(
    "/update",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseUpdateUser,
    response_model_exclude_none=True,
    description="Route for updating user",
)
async def req_update_user(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user: Annotated[
        UserToUpdate,
        Body(..., openapi_examples=get_user_update_examples()),
    ],
):
    return await update_user(
        settings=settings,
        db=db,
        token=token,
        user=user,
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseRemoveUser,
    response_model_exclude_none=True,
    description="Route for removing user",
)
async def req_user_remove(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: str = Depends(oauth2_scheme),
):
    return await remove_user(
        settings=settings,
        db=db,
        token=token,
    )
