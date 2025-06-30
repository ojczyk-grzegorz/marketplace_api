import datetime as dt

from fastapi import APIRouter, status, Query, Path, Body, Depends
from auth.auth import oauth2_scheme, validate_access_token, KEY, ALGORITHM

from db.db import database, db_search, db_insert, db_update, db_remove
from datamodels.response import ErrorResponse
from datamodels.item import (
    ItemDB,
    QueryItems,
    ItemsUser,
    ItemsQuery,
    ItemsCreate,
    ItemsCreated,
    ItemUpdate,
    ItemRemove,
)
from datamodels.user import UserDB
from testing.openapi.items import ITEM_CREATE, ITEM_PATCH


router = APIRouter(prefix="/items", tags=["Items"])


@router.get(
    "/query/{category}",
    status_code=status.HTTP_200_OK,
    # response_model=ItemsQuery | ErrorResponse,
    description="Query items based on various filters",
    response_model_exclude_none=True,
)
async def get_items(
    category: str = Path(...),
    query_items: QueryItems = Query(QueryItems()),
):
    
    category_id = db_search(
        f"""
        SELECT cid FROM categories WHERE name='{category}'
        """
    )[0][0] 

    results = db_search(
        f"""
        SELECT row_to_json(items) FROM items WHERE category_id = {category_id} LIMIT 10
        """
    )

    print(results)

    return results
       
    db_items: list[dict] = database["items"]

    items = []
    features = {
        **query_items.model_dump(exclude_none=True, exclude=["limit", "features"]),
        **(query_items.features or {}),
    }

    for item in db_items:
        qualified = True
        for key, value in features.items():
            if not qualified:
                break

            item_value = item.get(key, item["features_specific"].get(key))
            if item_value is None:
                qualified = False
            elif isinstance(value, list):
                if item_value not in value:
                    qualified = False
            elif isinstance(value, tuple):
                if value[0] > item_value or item_value > value[1]:
                    qualified = False
            elif value != item_value:
                qualified = False

        if qualified:
            items.append(item)

        if len(items) >= query_items.limit:
            break

    if not items:
        return ErrorResponse(
            error="ITEMS_NOT_FOUND",
            details={"query": query_items, "category": category},
        )

    return ItemsQuery(q=query_items, items=items)


@router.get(
    "/{iid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemDB | ErrorResponse,
    description="Get item by its ID",
)
async def get_item(iid: int = Path(...)):

    results = db_search(
        f"""
        SELECT json_agg(items) FROM items WHERE iid = {iid}
        """
    )[0][0]

    if results:
        return results[0]

    return ErrorResponse(
        error="ITEM_NOT_FOUND",
        details={"item_id": iid},
    )


@router.get(
    "/user/{uid}",
    status_code=status.HTTP_200_OK,
    response_model=ItemsUser | ErrorResponse,
    description="Get item by its ID",
)
async def get_user_items(uid: int = Path(...)):
    user = db_search(
        f"""
        SELECT json_agg(users) FROM users WHERE uid = {uid}
        """
    )[0][0]
    if not user:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": uid},
        )
    
    results = db_search(
        f"""
        SELECT json_agg(items) FROM items WHERE seller_id = {uid}
        """
    )[0][0]

    return ItemsUser(
        user=user[0],
        items=results
    )

    


@router.post(
    "/mine",
    status_code=status.HTTP_200_OK,
    response_model=ItemsUser | ErrorResponse,
    description="Get item by its ID",
)
async def get_user_items(token: str = Depends(oauth2_scheme)):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    user = db_search(
        f"""
        SELECT json_agg(users) FROM users WHERE uid = {user_id}
        """
    )[0][0]
    if not user:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )
    
    results = db_search(
        f"""
        SELECT json_agg(items) FROM items WHERE seller_id = {user_id}
        """
    )[0][0]

    return ItemsUser(
        user=user[0],
        items=results
    )


@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=ItemsCreated | ErrorResponse,
    description="Route for creating an item",
)
async def create_items(
    token: str = Depends(oauth2_scheme),
    req_body: ItemsCreate = Body(
        ...,
        openapi_examples=ITEM_CREATE,
    ),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    user = db_search(
        f"""
        SELECT json_agg(users) FROM users WHERE uid = {user_id}
        """
    )[0][0]
    if not user:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )
    
    items = []
    for n, item in enumerate(req_body.items):
        item = ItemDB(
            **item.model_dump(),
            seller_id=user_id,
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            expires_at=(
                dt.datetime.now(dt.timezone.utc)
                + dt.timedelta(days=item.expires_at_days)
            ).isoformat(),
        ).model_dump(exclude_none=True, mode="json")
        items.append(item)

    results = db_insert("items", items)

    return ItemsCreated(
        seller_id=user_id,
        items=results,
    )


@router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=ItemsCreated | ErrorResponse,
    description="Route for patching an item",
)
async def update_item(
    token: str = Depends(oauth2_scheme),
    item: ItemUpdate = Body(
        ...,
        openapi_examples=ITEM_PATCH,
    ),
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    user = db_search(
        f"""
        SELECT json_agg(users) FROM users WHERE uid = {user_id}
        """
    )[0][0]
    if not user:
        return ErrorResponse(
            error="USER_NOT_FOUND",
            details={"user_id": user_id},
        )
    item = ItemDB(
        **item.model_dump(),
        seller_id=user_id,
        created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        updated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        expires_at=(
            dt.datetime.now(dt.timezone.utc)
            + dt.timedelta(days=item.expires_at_days)
        ).isoformat(),
    ).model_dump(exclude_none=True, mode="json")

    results = db_update("items", item, f"seller_id = {user_id} AND iid = {item["iid"]}")[0]

    return ItemsCreated(
        seller_id=user_id,
        items=results
    )


@router.delete(
    "/remove",
    status_code=status.HTTP_200_OK,
    # response_model=ItemsCreated | ErrorResponse,
    description="Route for deleting an item",
)
async def remove_item(
    token: str = Depends(oauth2_scheme),
    req_body: ItemRemove = Body(...)
):
    user_id: int = validate_access_token(
        token=token,
        secret_key=KEY,
        algorithms=[ALGORITHM],
    )

    results =  db_remove("items", f"seller_id = {user_id} AND iid = {req_body.item_id}")
    return ItemsCreated(
        seller_id=user_id,
        items=results[0] if results else results
    )
