import uuid

from fastapi import HTTPException


class ExcInvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid credentials provided.")


class ExcUserNotFound(HTTPException):
    def __init__(self, user_id: uuid.UUID):
        super().__init__(status_code=404, detail=f"User with ID {user_id} not found.")
        self.user_id = user_id


class ExcUserExists(HTTPException):
    def __init__(self, email: str | None = None, phone: str | None = None):
        super().__init__(status_code=409, detail="User with provided values already exists.")
        self.email = email
        self.phone = phone


class ExcItemNotFound(HTTPException):
    def __init__(self, item_id: uuid.UUID):
        super().__init__(status_code=404, detail=f"Item with ID {item_id} not found.")
        self.item_id = item_id


class ExcTransactionActiveNotFound(HTTPException):
    def __init__(self, user_id: uuid.UUID, transaction_id: uuid.UUID):
        super().__init__(
            status_code=404,
            detail=f"Active transaction with ID {transaction_id} of user with ID {user_id} not found.",
        )
        self.transaction_id = transaction_id
        self.user_id = user_id


class ExcTransactionsActiveFound(HTTPException):
    def __init__(self, transaction_ids: list[str], user_id: uuid.UUID):
        super().__init__(
            status_code=404,
            detail=f"User with ID {user_id} has active transactions with IDs {transaction_ids}.",
        )
        self.transaction_ids = transaction_ids
        self.user_id = user_id


class ExcDiscountActiveNotFound(HTTPException):
    def __init__(self, discount_code: str):
        super().__init__(
            status_code=404,
            detail=f"Active discount with code {discount_code} not found.",
        )
        self.discount_code = discount_code


class ExcDeliveryOptionNotFound(HTTPException):
    def __init__(self, delivery_option_id: uuid.UUID):
        super().__init__(
            status_code=404,
            detail=f"Active discount with code {delivery_option_id} not found.",
        )
        self.delivery_option_id = delivery_option_id


class ExcTransactionFinalizedNotFound(HTTPException):
    def __init__(self, user_id: uuid.UUID, transaction_id: uuid.UUID):
        super().__init__(
            status_code=404,
            detail=f"Active transaction with ID {transaction_id} of user with ID {user_id} not found.",
        )
        self.transaction_id = transaction_id
        self.user_id = user_id


class ExcInsufficientStock(HTTPException):
    def __init__(self, item_id: uuid.UUID, requested: int, available: int):
        super().__init__(
            status_code=400,
            detail=f"Insufficient stock for item with ID {item_id}. Requested: {requested}, Available: {available}.",
        )
        self.item_id = item_id
        self.requested = requested
        self.available = available
