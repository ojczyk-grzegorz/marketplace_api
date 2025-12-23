import datetime as dt
from decimal import Decimal
import uuid

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlmodel import CheckConstraint, Field, SQLModel


class DBItem(SQLModel, table=True):
    __tablename__ = "items"
    __table_args__ = (CheckConstraint("stock >= 0", name="check_stock_non_negative"),)

    item_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(String(256), nullable=False))
    category: str = Field(sa_column=Column(String(32), nullable=False))
    subcategories: list[str] | None = Field(
        sa_column=Column(ARRAY(String(32)), nullable=True), default=None
    )
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    brand: str | None = Field(
        sa_column=Column(String(128), nullable=True), default=None
    )
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    stock: int = Field(sa_column=Column(Integer, nullable=False))


class DBUser(SQLModel, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    email: str = Field(sa_column=Column(String(256), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(16), unique=True, nullable=False))
    password_hash: str = Field(
        sa_column=Column(String(64), nullable=False), exclude=True
    )
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class DBItemSnapshot(SQLModel, table=True):
    __tablename__ = "items_snapshots"

    item_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True))
    name: str = Field(sa_column=Column(String(256), nullable=False))
    category: str | None = Field(
        sa_column=Column(String(32), nullable=True), default=None
    )
    subcategories: str | None = Field(
        sa_column=Column(String(32), nullable=True), default=None
    )  # Note: single string in snapshots
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    brand: str | None = Field(
        sa_column=Column(String(128), nullable=True), default=None
    )
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), primary_key=True)
    )


class DBGroundStaff(SQLModel, table=True):
    __tablename__ = "ground_staff"

    staff_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(String(128), nullable=False))
    role: str = Field(sa_column=Column(String(64), nullable=False))


class DBDeliveryOptions(SQLModel, table=True):
    __tablename__ = "delivery_options"

    option_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(String(64), nullable=False))
    contractor_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBDiscount(SQLModel, table=True):
    __tablename__ = "discounts"

    discount_code: str = Field(sa_column=Column(String(128), primary_key=True))
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    valid_from: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    valid_to: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    discount_percentage: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    item_ids: list[uuid.UUID] | None = Field(
        sa_column=Column(ARRAY(UUID(as_uuid=True)), nullable=True), default=None
    )
    brands: list[str] | None = Field(
        sa_column=Column(ARRAY(String(128)), nullable=True), default=None
    )
    categories: dict | None = Field(
        sa_column=Column(JSONB, nullable=True), default=None
    )


class DBTransaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    user_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    created_at: dt.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ), default_factory=lambda: dt.datetime.now(dt.timezone.utc),
    )
    delivery_option_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    transaction_details: dict = Field(sa_column=Column(JSONB, nullable=False))
    total_price: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBTransactionDiscount(SQLModel, table=True):
    __tablename__ = "transaction_discounts"

    row_id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    discount_code: str = Field(sa_column=Column(String(128), nullable=False))


class DBTransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"

    row_id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    item_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    item_updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    count: int = Field(sa_column=Column(Integer, nullable=False))
    price_after_discounts: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBTransactionAction(SQLModel, table=True):
    __tablename__ = "transaction_actions"

    action_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    action: str = Field(sa_column=Column(String(64), nullable=False))
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    performed_by: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False)
    )
    performed_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class DBTransactionFinalized(SQLModel, table=True):
    __tablename__ = "transactions_finalized"

    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    user_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    finalized_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    delivery_option: str = Field(sa_column=Column(String(32), nullable=False))
    delivery_price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    transaction_details: dict = Field(sa_column=Column(JSONB, nullable=False))
    items: dict = Field(
        sa_column=Column(JSONB, nullable=False),
    )
    action_history: dict = Field(sa_column=Column(JSONB, nullable=False))
