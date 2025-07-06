import random
from datetime import datetime, timedelta, timezone
import json
from uuid import uuid4

import psycopg2

from app.utils.auth import get_password_hash

from postgres.mock_values import (
    CITIES,
    STREETS,
    FIRST_NAMES,
    LAST_NAMES,
    CATEGORIES,
    TYPES,
    STYLES,
    BRANDS,
    CONDITIONS,
    MATERIALS,
    COLORS,
    PATTERNS,
    WIDTHS,
    FASTENERS,
    HEELS,
    TOES,
    DESCRIPTIONS
)


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)


TODAY = datetime(2025, 6, 11, tzinfo=timezone.utc)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)


def get_mock_users(user_count: int) -> list[dict]:
    users = []
    n = 0
    for first_name in FIRST_NAMES:
        for last_name in LAST_NAMES:
            created_at = random_date(SIX_MONTHS_AGO, TODAY)
            user = dict(
                uid=n + 1,
                uid_uuid4=uuid4().hex,
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone=f"+48{random.randint(500000000, 799999999)}",
                password_hash=get_password_hash("password"),
                first_name=first_name,
                last_name=last_name,
                birth_date=random_date(
                    datetime(1975, 1, 1), datetime(2009, 12, 31)
                ).strftime("%Y-%m-%d"),
                country="PL",
                city=random.choice(CITIES),
                street=random.choice(STREETS),
                street_number=str(random.randint(1, 200)),
                postal_code=f"{random.randint(10, 99)}-{random.randint(100, 999)}",
                created_at=created_at.isoformat(),
                updated_at=created_at.isoformat(),
            )
            users.append(user)
            n += 1
            if n >= user_count:
                break
        if n >= user_count:
            break
    return users


def get_mock_items(item_count: int, users: list[dict]) -> list[dict]:
    items = []
    for n in range(item_count):
        seller = users[random.randint(0, len(users) // 3)]

        brand = random.choice(BRANDS)
        category = random.choice(CATEGORIES)
        material = random.choice(MATERIALS)
        color = random.choice(COLORS)

        features = dict(
            type=random.choice(TYPES),
            style=random.choice(STYLES),
            condition=random.choice(CONDITIONS),
            pattern=random.choice(PATTERNS),
            size=float(random.randint(30, 60)),
            width=random.choice(WIDTHS),
            fastener=random.choice(FASTENERS),
            heel=random.choice(HEELS),
            toe=random.choice(TOES),
        )

        created_at = random_date(datetime.fromisoformat(seller["created_at"]), TODAY)

        joins_sent = ["\n", ".\n", ". "]
        joins_kv = [" ", " ", ": ", ":", " - ", "-"]
        join_kv: str = random.choice(joins_kv)
        join_sent: str = random.choice(joins_sent)
        desc = list(set(random.choices(DESCRIPTIONS, k=random.randint(2, 6))))
        feat = list(set(random.choices(list(features.items()), k=len(desc) - 1)))
        description = []
        for d, f in zip(desc, feat):
            (description.append(d),)
            description.append(join_kv.join([str(x) for x in f]))
        description.append(desc[-1])
        description = join_sent.join(description)

        item = dict(
            iid=n + 1,
            iid_uuid4=uuid4().hex,
            name=f"{brand} {color} {material} {category}",
            seller_id=seller["uid"],
            price=float(random.randint(10, 300)),
            brand=brand,
            category=category,
            material=material,
            color=color,
            **features,
            country=seller["country"],
            city=seller["city"],
            created_at=created_at.isoformat(),
            updated_at=created_at.isoformat(),
            expires_at=(
                created_at + timedelta(days=random.randint(15, 60))
            ).isoformat(),
            description=description,
        )
        items.append(item)
    return items


def get_mock_transactions(transaction_count: int, users: list[dict], items: list[dict]) -> list[dict]:
    transactions = []
    for n in range(transaction_count):
        item: dict = items.pop()

        for user in users:
            if user["uid"] == item["seller_id"]:
                seller = user
                break

        while True:
            buyer = random.choice(users)
            if buyer != seller:
                break

        sold_at = random_date(
            datetime.fromisoformat(item["created_at"]),
            TODAY,
        )
        finilized = random_date(
            sold_at,
            TODAY,
        ).isoformat()
        transaction = dict(
            tid=n + 1,
            tid_uuid4=uuid4().hex,
            sold_at=sold_at.isoformat(),
            item=item,
            seller_uid_uuid4=seller["uid_uuid4"],
            buyer_uid_uuid4=buyer["uid_uuid4"],
            seller_snapshot=seller,
            buyer_snapshot=buyer,
            finilized=random.choice([finilized, finilized, finilized, finilized, None]),
        )
        transactions.append(transaction)
    return transactions

