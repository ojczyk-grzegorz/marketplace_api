from typing import Annotated
import uuid

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.routing import APIRoute
from sqlmodel import Session

from app.auth.utils import oauth2_scheme
from app.configs.datamodels import Settings
from app.configs.utils import get_settings
from app.database.utils import get_db_session
from app.routers.transactions.datamodels import (
    ResponseGetAllCurrentTransactions,
    ResponseGetCurrentTransaction,
    TransactionToCreate,
)
from app.routers.transactions.service import (
    create_transaction,
    get_all_current_transactions,
    get_current_transaction,
)
from testing.openapi_examples import get_transaction_create_examples

router = APIRouter(prefix="/transactions", tags=["Transactions"], route_class=APIRoute)


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ResponseGetCurrentTransaction,
    response_model_exclude_none=True,
    description="Route for creating new transaction",
)
async def transaction_create(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    req_body: Annotated[
        TransactionToCreate,
        Body(..., openapi_examples=get_transaction_create_examples()),
    ],
):
    return await create_transaction(
        settings=settings,
        db=db,
        token=token,
        req_body=req_body,
    )


@router.get(
    "/current",
    status_code=status.HTTP_200_OK,
    response_model=ResponseGetAllCurrentTransactions,
    response_model_exclude_none=True,
    description="Route for retrieving current user's transactions",
)
async def transactions_get_current(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: str = Depends(oauth2_scheme),
):
    return await get_all_current_transactions(
        settings=settings,
        db=db,
        token=token,
    )


@router.get(
    "/current/{transaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseGetCurrentTransaction,
    response_model_exclude_none=True,
    description="Route for retrieving transaction status",
)
async def transaction_get_status(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    transaction_id: Annotated[
        uuid.UUID, Path(..., description="The UUID of the transaction to retrieve")
    ],
):
    return await get_current_transaction(
        settings=settings,
        db=db,
        token=token,
        transaction_id=transaction_id,
    )
