import datetime as dt


class ExcInvalidCredentials(Exception):
    def __init__(self):
        super().__init__("Invalid credentials provided.")


class ExcUserNotFound(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.log_args = {"user_id": user_id}
        super().__init__(f"User with ID {user_id} not found.")


class ExcUserExists(Exception):
    def __init__(self, email: str | None = None, phone: str | None = None):
        self.email = email
        self.phone = phone
        self.log_args = {"email": email, "phone": phone}

        message = "User with provided values already exists."
        if email:
            message += f" Email: {email}."
        if phone:
            message += f" Phone: {phone}."
        super().__init__(message)


class ExcTransactionsFound(Exception):
    def __init__(self, user_id: int, details: dict):
        self.details = details
        self.log_args = {"user_id": user_id, "details": details}

        super().__init__(
            f"User with ID {user_id} has active transactions and cannot be removed."
        )


class ExcTransactionActiveNotFound(Exception):
    def __init__(self, transaction_id: int, user_id_uuid4: str):
        self.transaction_id = transaction_id
        self.user_id_uuid4 = user_id_uuid4

        self.log_args = {"transaction_id": transaction_id, "user_id": user_id_uuid4}

        message = f"Active transaction with ID {transaction_id} of user ID {user_id_uuid4} not found."
        if user_id_uuid4 is not None:
            message += f" User ID: {user_id_uuid4}."

        super().__init__(message)


class ExcItemNotFound(Exception):
    def __init__(
        self, item_id: str, user_id: int | None = None, not_user_id: int | None = None
    ):
        self.item_id = item_id
        self.user_id = user_id
        self.not_user_id = not_user_id

        self.log_args = {
            "item_id": item_id,
            "user_id": user_id,
            "not_user_id": not_user_id,
        }

        message = f"Item with ID {item_id} not found."
        if user_id is not None:
            message += f" User ID: {user_id}."
        if not_user_id is not None:
            message += f" Not User ID: {not_user_id}."

        super().__init__(message)


class ExcInvalidExpiresAt(Exception):
    def __init__(self, expires_at: str):
        self.current_time = dt.datetime.now(dt.timezone.utc)
        self.expires_at: dt.datetime = expires_at

        self.log_args = {
            "expires_at": expires_at,
            "current_time": self.current_time.isoformat(),
        }

        super().__init__(
            f"Expiration date {expires_at.isoformat()} must be in the future. Current time is {self.current_time.isoformat()}."
        )
