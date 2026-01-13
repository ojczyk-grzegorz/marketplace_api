import datetime as dt
from decimal import Decimal
import uuid

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlmodel import CheckConstraint, Field, ForeignKey, SQLModel


class DBItem(SQLModel, table=True):
    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
        CheckConstraint("price > 0", name="check_price_positive"),
    )

    item_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True),
        default_factory=uuid.uuid4,
    )
    name: str = Field(sa_column=Column(String(256), nullable=False))
    category: str = Field(sa_column=Column(String(32), nullable=False))
    subcategories: list[str] | None = Field(
        sa_column=Column(ARRAY(String(32)), nullable=True), default=None
    )
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    brand: str | None = Field(sa_column=Column(String(128), nullable=True), default=None)
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    stock: int = Field(sa_column=Column(Integer, nullable=False))


class DBUser(SQLModel, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True),
        default_factory=uuid.uuid4,
    )
    email: str = Field(sa_column=Column(String(256), unique=True, nullable=False))
    phone: str = Field(sa_column=Column(String(16), unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String(64), nullable=False), exclude=True)
    created_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))


class DBItemSnapshot(SQLModel, table=True):
    __tablename__ = "items_snapshots"

    item_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True))
    updated_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), primary_key=True))

    name: str = Field(sa_column=Column(String(256), nullable=False))
    category: str | None = Field(sa_column=Column(String(32), nullable=True), default=None)
    subcategories: list[str] | None = Field(sa_column=Column(ARRAY(String(32)), default=None))
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    brand: str | None = Field(sa_column=Column(String(128), nullable=True), default=None)
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    features: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)
    created_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))


class DBGroundStaff(SQLModel, table=True):
    __tablename__ = "ground_staff"

    staff_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True),
        default_factory=uuid.uuid4,
    )
    name: str = Field(sa_column=Column(String(128), nullable=False))
    role: str = Field(sa_column=Column(String(64), nullable=False))


class DBDeliveryOptions(SQLModel, table=True):
    __tablename__ = "delivery_options"

    option_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True),
        default_factory=uuid.uuid4,
    )
    name: str = Field(sa_column=Column(String(64), nullable=False))
    contractor_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    price: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBDiscount(SQLModel, table=True):
    __tablename__ = "discounts"
    __table_args__ = (
        CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="check_discount_percentage_range",
        ),
        CheckConstraint("valid_from < valid_to", name="check_valid_date_range"),
    )

    discount_code: str = Field(sa_column=Column(String(128), primary_key=True))
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    valid_from: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    valid_to: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    discount_percentage: Decimal = Field(sa_column=Column(Numeric, nullable=False))
    item_ids: list[uuid.UUID] | None = Field(
        sa_column=Column(ARRAY(UUID(as_uuid=True)), nullable=True), default=None
    )
    brands: list[str] | None = Field(
        sa_column=Column(ARRAY(String(128)), nullable=True), default=None
    )
    categories: dict | None = Field(sa_column=Column(JSONB, nullable=True), default=None)


class DBTransaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
        )
    )
    created_at: dt.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
        default_factory=lambda: dt.datetime.now(dt.timezone.utc),
    )
    delivery_option_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True), ForeignKey("delivery_options.option_id"), nullable=False
        )
    )
    name: str = Field(sa_column=Column(String(256), nullable=False))
    last_name: str = Field(sa_column=Column(String(256), nullable=False))
    email: str = Field(sa_column=Column(String(256), nullable=False))
    phone: str = Field(sa_column=Column(String(16), nullable=False))
    country: str = Field(sa_column=Column(String(128), nullable=False))
    city: str = Field(sa_column=Column(String(128), nullable=False))
    postal_code: str = Field(sa_column=Column(String(16), nullable=False))
    address_line_1: str = Field(sa_column=Column(String(256), nullable=False))
    address_line_2: str | None = Field(sa_column=Column(String(256), nullable=True), default=None)
    total_price: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBTransactionDiscount(SQLModel, table=True):
    __tablename__ = "transaction_discounts"

    row_id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    transaction_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    discount_code: str = Field(
        sa_column=Column(String(128), ForeignKey("discounts.discount_code"), nullable=False)
    )


class DBTransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"
    __table_args__ = (
        CheckConstraint("count > 0", name="check_count_positive"),
        CheckConstraint("price_after_discounts >= 0", name="check_price_non_negative"),
    )

    row_id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    transaction_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    item_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("items.item_id"), nullable=False)
    )
    updated_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    count: int = Field(sa_column=Column(Integer, nullable=False))
    price_after_discounts: Decimal = Field(sa_column=Column(Numeric, nullable=False))


class DBTransactionAction(SQLModel, table=True):
    __tablename__ = "transaction_actions"

    action_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    transaction_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    action: str = Field(sa_column=Column(String(64), nullable=False))
    description: str | None = Field(sa_column=Column(Text, nullable=True), default=None)
    performed_by: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    performed_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))


class DBTransactionFinalized(SQLModel, table=True):
    __tablename__ = "transactions_finalized"

    transaction_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True))
    user_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    created_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    finalized_at: dt.datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    total_price: Decimal = Field(sa_column=Column(Numeric, nullable=False))

    name: str = Field(sa_column=Column(String(256), nullable=False))
    last_name: str = Field(sa_column=Column(String(256), nullable=False))
    email: str = Field(sa_column=Column(String(256), nullable=False))
    phone: str = Field(sa_column=Column(String(16), nullable=False))
    country: str = Field(sa_column=Column(String(128), nullable=False))
    city: str = Field(sa_column=Column(String(128), nullable=False))
    postal_code: str = Field(sa_column=Column(String(16), nullable=False))
    address_line_1: str = Field(sa_column=Column(String(256), nullable=False))
    address_line_2: str | None = Field(sa_column=Column(String(256), nullable=True), default=None)

    delivery: dict = Field(sa_column=Column(JSONB, nullable=False))
    items: list[dict] = Field(sa_column=Column(JSONB, nullable=False))
    action_history: list[dict] = Field(sa_column=Column(JSONB, nullable=False))
