from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.datamodels.auth import BearerToken
from app.datamodels.configs import Settings
from app.services.auth.service import get_token
from app.utils.configs import get_settings
from app.utils.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=APIRoute)


@router.post(
    "/token",
    status_code=status.HTTP_200_OK,
    response_model=BearerToken,
    description="Route for getting user token",
)
async def req_get_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
):
    return await get_token(settings=settings, db=db, form=form)
