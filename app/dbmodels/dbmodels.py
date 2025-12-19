import datetime as dt
from decimal import Decimal

from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy import Column, String, Text, Numeric, DateTime
import uuid


class ItemSQL(SQLModel, table=True):
    __tablename__ = "items"

    item_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(String(256), nullable=False))
    category: str = Field(sa_column=Column(String(32), nullable=False))
    subcategories: list[str] | None = Field(
        sa_column=Column(ARRAY(String(32)), nullable=True), default=None
    )
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    brand: str | None = Field(sa_column=Column(String(64), nullable=True), default=None)
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True)))


class UserSQL(SQLModel, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    email: str = Field(sa_column=Column(String(256), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(16), unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String(64), nullable=False))
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ItemSnapshotSQL(SQLModel, table=True):
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
    brand: str | None = Field(sa_column=Column(String(64), nullable=True), default=None)
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), primary_key=True)
    )


class GroundStaffSQL(SQLModel, table=True):
    __tablename__ = "ground_staff"

    staff_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(String(128), nullable=False))
    role: str = Field(sa_column=Column(String(64), nullable=False))


class TransactionSQL(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    )
    user_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    delivery_option: str = Field(sa_column=Column(String(32), nullable=False))
    delivery_price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    transaction_details: dict = Field(sa_column=Column(JSONB, nullable=False))


class TransactionItemSQL(SQLModel, table=True):
    __tablename__ = "transaction_items"

    transaction_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    item_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True))
    item_updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), primary_key=True)
    )
    discount_amount: Decimal | None = Field(
        sa_column=Column(Numeric, nullable=True), default=None
    )
    discount_code: str | None = Field(
        sa_column=Column(String(64), nullable=True), default=None
    )


class TransactionActionSQL(SQLModel, table=True):
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


class TransactionFinalizedSQL(SQLModel, table=True):
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
    items: dict = Field(sa_column=Column(JSONB, nullable=False))
    action_history: dict = Field(sa_column=Column(JSONB, nullable=False))
