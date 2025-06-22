import random
from datetime import datetime, timedelta
import json
import os

from mock_values.common import CITIES, STREETS
from mock_values.users import FIRST_NAMES, LAST_NAMES, USER_REVIEWS
from mock_values.items import (
    CATEGORIES,
    SIZES,
    STYLES,
    CONDITIONS,
    MATERIALS,
    COLORS,
    BRANDS,
    PATTERNS,
    DESCRIPTIONS,
    DELIVERIES,
)


dir_files_db = "db/mock_data"
os.makedirs(dir_files_db, exist_ok=True)

filepath_users = os.path.join(dir_files_db, "users.json")
filepath_categories = os.path.join(dir_files_db, "categories.json")
filepath_items = os.path.join(dir_files_db, "items.json")
filepath_transactions = os.path.join(dir_files_db, "transactions.json")

today = datetime(2025, 6, 11)
six_months_ago = today - timedelta(days=180)
one_year_ago = today - timedelta(days=365)


# Helper function to generate random dates for history
def random_date(start_date, end_date):
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)


def main():
    random.seed(0)

    ########### CUSTOMERS ###########
    users = []
    n = 0
    for first_name in FIRST_NAMES:
        for last_name in LAST_NAMES:
            reviews = list(set(random.choices(USER_REVIEWS, k=random.randint(0, 20))))
            created_at = random_date(six_months_ago, today)
            customer = {
                "uid": n,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "password_hash": f"password_hash{n}",
                "phone": f"+48{random.randint(500000000, 799999999)}",
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": random_date(
                    datetime(1975, 1, 1), datetime(2009, 12, 31)
                ).strftime("%Y-%m-%d"),
                "country": "Poland",
                "city": random.choice(CITIES),
                "street": random.choice(STREETS),
                "street_number": str(random.randint(1, 200)),
                "postal_code": f"{random.randint(10, 99)}-{random.randint(100, 999)}",
                "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "updated_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "last_activity": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "reviews": [
                    {
                        "rating": review[0],
                        "comment": review[1],
                        "created_at": random_date(created_at, today).strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        ),
                    }
                    for review in reviews
                ],
                "rating": round(sum(review[0] for review in reviews) / len(reviews), 1)
                if reviews
                else 0.0,
                "avatar": None,
            }
            n += 1
            users.append(customer)

    with open(filepath_users, "w") as file:
        json.dump(users, file, indent=4)

    print("Users generated:", len(users))

    ########### CATEGORIES ###########

    categories = []
    for n, category in enumerate(CATEGORIES):
        categories.append(
            {
                "cid": n,
                "name": category,
            }
        )
    with open(filepath_categories, "w") as file:
        json.dump(categories, file, indent=4)

    print("Categories generated:", len(categories))

    ########### ITEMS ###########

    items = []
    for n in range(5_000):
        iid = n

        category = random.choice(categories)
        seller = users[random.randint(0, len(users) // 3)]
        subcategory = random.choice(CATEGORIES[category["name"]])

        price = float(random.randint(1, 300))
        condition = random.choice(CONDITIONS)
        brand = random.choice(BRANDS)
        material = random.choice(MATERIALS)
        color = random.choice(COLORS)
        pattern = random.choice(PATTERNS)
        size = random.choice(SIZES)
        style = random.choice(STYLES)

        features_common = {}
        for feature, values in subcategory.get("features_common", {}).items():
            features_common[feature] = random.choice(values)

        features_specific = {}
        for feature, values in subcategory.get("features_specific", {}).items():
            features_specific[feature] = random.choice(values)

        features = {
            **features_common,
            **features_specific,
        }

        created_at = random_date(one_year_ago, today)
        updated_at = created_at
        expires_at = created_at + timedelta(days=random.randint(15, 60))

        name = f"{brand} {color} {subcategory['name']}"

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

        item = {
            "iid": iid,
            "name": name,
            "cid": category["cid"],
            "seller_id": seller["uid"],
            "seller_rating": seller["rating"],
            "subcategory": subcategory["name"],
            "price": price,
            "condition": condition,
            "brand": brand,
            "material": material,
            "color": color,
            "pattern": pattern,
            "size": size,
            "style": style,
            "features_specific": features_specific,
            "city": seller["city"],
            "street": seller["street"],
            "delivery": list(
                set(random.choices(DELIVERIES, k=random.randint(1, len(DELIVERIES))))
            ),
            "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "icon": None,
            "images": [],
            "interested": random.randint(0, 30),
            "description": description,
            **features_common,
        }

        items.append(item)

    with open(filepath_items, "w") as file:
        json.dump(items, file, indent=4)

    print("Items generated:", len(items))

    ########### TRANSACTIONS ###########
    transactions = []
    for n in range(4_000):
        item: dict = items.pop()

        while True:
            customer_id = random.choice(users)["uid"]
            if customer_id != item["seller_id"]:
                break

        transaction_date = random_date(
            datetime.fromisoformat(item["created_at"]),
            datetime.fromisoformat(item["expires_at"]),
        )

        transaction = {
            "tid": n,
            "name": item["name"],
            "seller_id": item["seller_id"],
            "date": transaction_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "buyer": customer_id,
            "item": item,
        }
        transactions.append(transaction)

    with open(filepath_transactions, "w") as file:
        json.dump(transactions, file, indent=4)

    print("Transactions generated:", len(transactions))


if __name__ == "__main__":
    main()
