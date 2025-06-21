import random
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

dir_files_db = "db/mock_data"
os.makedirs(dir_files_db, exist_ok=True)

filepath_items = os.path.join(dir_files_db, "items.json")
filepath_users = os.path.join(dir_files_db, "users.json")
filepath_transactions = os.path.join(dir_files_db, "transactions.json")

today = datetime(2025, 6, 11)
six_months_ago = today - timedelta(days=180)
one_year_ago = today - timedelta(days=365)


# polish cities
cities = [
    "Warsaw",
    "Kraków",
    "Łódź",
    "Wrocław",
    "Poznań",
    "Gdańsk",
    "Szczecin",
    "Bydgoszcz",
    "Lublin",
    "Białystok",
    "Katowice",
    "Gdynia",
    "Częstochowa",
    "Radom",
    "Sosnowiec",
    "Toruń",
    "Kielce",
    "Gliwice",
    "Zabrze",
    "Olsztyn",
    "Bielsko-Biała",
    "Rzeszów",
    "Ruda Śląska",
    "Rybnik",
    "Dąbrowa Górnicza",
    "Elbląg",
    "Płock",
    "Opole",
    "Zielona Góra",
]

streets = [
    "Kwiatowa",
    "Słoneczna",
    "Leśna",
    "Polna",
    "Wiosenna",
    "Złota",
    "Srebrna",
    "Brązowa",
    "Różana",
    "Jasna",
    "Ciemna",
    "Węgierska",
    "Polska",
    "Francuska",
    "Hiszpańska",
    "Włoska",
    "Niemiecka",
    "Angielska",
    "Szwedzka",
    "Norweska",
    "Fińska",
    "Duńska",
    "Rosyjska",
    "Ukraińska",
    "Białoruska",
    "Czeska",
    "Słowacka",
    "Węgierska",
    "Rumuńska",
    "Bułgarska",
    "Serbska",
    "Chorwacka",
    "Słoweńska",
    "Grecka",
    "Turecka",
    "Cypryjska",
    "Portugalska",
    "Hiszpańska",
    "Włoska",
    "Francuska",
    "Belgijska",
    "Holenderska",
    "Szwajcarska",
    "Australijska",
    "Kanadyjska",
    "Amerykańska",
    "Argentyńska",
    "Brazylijska",
]


# polish first names
first_names = [
    "Jakub",
    "Zuzanna",
    "Kacper",
    "Julia",
    "Michał",
    "Zofia",
    "Szymon",
    "Maja",
    "Filip",
    "Hanna",
    "Aleksander",
    "Wiktoria",
    "Antoni",
    "Natalia",
    "Jan",
    "Emilia",
    "Wojciech",
    "Lena",
    "Mateusz",
    "Oliwia",
    "Piotr",
    "Amelia",
    "Kamil",
    "Martyna",
    "Tomasz",
    "Karolina",
    "Adam",
    "Klaudia",
    "Paweł",
    "Alicja",
    "Rafał",
    "Weronika",
    "Marek",
    "Magdalena",
    "Grzegorz",
    "Ewa",
    "Marcin",
    "Agata",
    "Łukasz",
    "Anna",
    "Dawid",
    "Katarzyna",
    "Bartosz",
    "Joanna",
    "Sebastian",
    "Gabriela",
    "Dominik",
    "Patrycja",
    "Artur",
    "Monika",
    "Michał",
    "Justyna",
    "Krzysztof",
    "Barbara",
    "Sławomir",
    "Elżbieta",
]

# polish last names
last_names = [
    "Nowak",
    "Kowalski",
    "Wiśniewski",
    "Wójcik",
    "Kowalczyk",
    "Kamiński",
    "Lewandowski",
    "Zieliński",
    "Szymański",
    "Woźniak",
    "Dąbrowski",
    "Kozłowski",
    "Jankowski",
    "Witkowski",
    "Mazur",
    "Krawczyk",
    "Piotrowski",
    "Grabowski",
    "Zając",
    "Pawlak",
    "Michalski",
    "Król",
    "Wieczorek",
    "Jasiński",
    "Olszewski",
    "Baran",
    "Sikora",
    "Walczak",
    "Kubiak",
    "Wysocki",
    "Czarnecki",
    "Kucharski",
    "Sadowski",
    "Wojciechowski",
    "Bąk",
    "Kaczmarek",
    "Pietrzak",
    "Nowicki",
    "Szulc",
    "Wasilewski",
    "Kalinowski",
    "Ciesielski",
    "Klimczak",
    "Wojtasik",
    "Zalewski",
    "Kowalewski",
    "Szczepaniak",
    "Błaszczyk",
    "Kowal",
    "Górski",
    "Jabłoński",
    "Kozak",
    "Sienkiewicz",
    "Wysocka",
    "Krawczyk",
]

users_reviews = [
    (4.5, "Great quality and fast delivery!"),
    (4.0, "Good product, but the size was a bit off."),
    (5.0, "Absolutely love it! Will buy again."),
    (3.5, "Decent item, but expected better quality."),
    (4.5, "Exceeded my expectations! Highly recommend."),
    (2.0, "Not what I expected, quite disappointed."),
    (4.0, "Nice design and comfortable to wear."),
    (3.0, "Average quality, nothing special."),
    (5.0, "Perfect fit and great value for money!"),
    (4.0, "Good product, but delivery took longer than expected."),
    (3.5, "Okay quality, but the color was different from the picture."),
    (4.5, "Very satisfied with my purchase!"),
    (2.5, "Not worth the price, quality could be better."),
    (4.0, "Stylish and comfortable, would recommend."),
    (3.0, "It's okay, but I've seen better."),
    (5.0, "Fantastic item! Will definitely buy again."),
    (4.5, "Great value for money and fast shipping!"),
    (3.5, "Good quality, but the fit was a bit tight."),
    (4.0, "Really happy with this purchase!"),
    (2.0, "Disappointed with the quality, won't buy again."),
    (4.5, "Loved the design and the comfort!"),
    (3.0, "It's fine, but I expected more."),
    (5.0, "Best purchase I've made in a while!"),
    (4.0, "Good quality, but the delivery was slow."),
    (3.5, "Nice item, but not as described."),
    (4.5, "Very happy with my order!"),
    (2.5, "Quality is not great for the price."),
    (4.0, "Stylish and comfortable, would buy again."),
    (3.0, "It's okay, but I've seen better options."),
    (5.0, "Absolutely love it! Perfect fit and quality."),
    (4.5, "Great product, fast delivery, very satisfied!"),
    (3.5, "Decent quality, but the color was off."),
    (4.0, "Good item, but expected better quality."),
    (2.0, "Not worth the price, quite disappointed."),
    (4.5, "Exceeded my expectations! Highly recommend."),
    (3.0, "Average quality, nothing special."),
    (5.0, "Perfect fit and great value for money!"),
    (4.0, "Nice design and comfortable to wear."),
]

categories = {
    "clothes": {
        "T-Shirt": {
            "size": ["S", "M", "L", "XL"],
            "pattern": ["Solid", "Striped", "Graphic"],
            "fit": ["Regular", "Slim", "Loose"],
            "sleeve": ["Short", "Long", "Sleeveless"],
            "collar": ["Crew", "V-Neck", "Polo"],
            "price": [
                10.99,
                15.99,
                20.99,
                25.99,
                30.99,
                35.99,
                40.99,
                45.99,
                50.99,
                55.99,
                60.99,
            ],
        },
        "Trousers": {
            "size": ["S", "M", "L", "XL"],
            "pattern": ["Solid", "Checked", "Denim"],
            "length": ["Short", "Regular", "Long"],
            "fit": ["Regular", "Slim", "Loose"],
            "shape": ["Straight", "Bootcut", "Skinny"],
            "raise": ["High", "Mid", "Low"],
            "price": [
                20.99,
                25.99,
                30.99,
                35.99,
                40.99,
                45.99,
                50.99,
                55.99,
                60.99,
                65.99,
            ],
        },
    },
    "shoes": {
        "Sneakers": {
            "size": ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"],
            "color": ["Black", "White", "Red", "Blue", "Green"],
            "material": ["Leather", "Canvas", "Synthetic"],
            "price": [
                29.99,
                34.99,
                39.99,
                44.99,
                49.99,
                54.99,
                59.99,
                64.99,
                69.99,
                74.99,
            ],
        },
        "Boots": {
            "size": ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"],
            "color": ["Black", "Brown", "Tan"],
            "material": ["Leather", "Suede"],
            "style": ["Ankle Boots", "Knee-High Boots"],
            "price": [
                49.99,
                59.99,
                69.99,
                79.99,
                89.99,
                99.99,
                109.99,
                119.99,
                129.99,
                139.99,
            ],
        },
    },
}

condtions = ["New", "Not Used", "Very Good", "Good", "Fair", "Poor"]
types = ["Casual", "Sporty", "Fashion"]
materials = ["Cotton", "Polyester", "Wool", "Leather", "Denim", "Linen"]
colors = ["Red", "Blue", "Green", "Black", "White", "Yellow", "Pink", "Purple"]
brands = [
    "Aetheria Apparel",
    "Terra Nova Threads",
    "Vesper Collective",
    "Kinetic Stitch",
    "Obsidian Weave",
    "Luminary Loft",
    "Solstice Supply Co.",
    "Echo Garb",
    "Summit & Spoke",
    "Meridian Mode",
    "Wilde Folk Goods",
    "Cascade Clothiers",
    "Phantom Fit",
    "Nova Bloom",
    "Evergreen & Elm",
]
patterns = ["Solid", "Striped", "Checked", "Floral", "Geometric", "Graphic"]
descriptions = [
    "A stylish and comfortable piece for everyday wear",
    "Perfect for casual outings or lounging at home",
    "Crafted with high-quality materials for durability",
    "A versatile item that can be dressed up or down",
    "Designed with a modern aesthetic in mind",
    "Ideal for layering or wearing on its own",
    "Features unique details that set it apart from the rest",
    "A must-have addition to any wardrobe",
    "Combines fashion and functionality seamlessly",
    "An essential piece for any fashion-forward individual",
    "Offers a perfect blend of comfort and style",
    "A timeless design that never goes out of fashion",
    "Made with sustainable practices in mind",
    "A statement piece that adds flair to any outfit",
    "Lightweight and breathable for all-day comfort",
    "Available in a range of sizes to fit every body type",
    "A classic design with a contemporary twist",
    "Perfect for transitioning between seasons",
    "A unique blend of colors and patterns for a standout look",
    "Crafted with attention to detail and quality craftsmanship",
    "A piece that tells a story with its design and materials",
    "An item that embodies the spirit of adventure and exploration",
    "A fusion of traditional and modern styles",
    "A piece that celebrates individuality and self-expression",
    "A versatile item that can be styled in multiple ways",
    "A piece that brings a touch of elegance to any outfit",
    "A comfortable and chic option for any occasion",
    "A piece that inspires confidence and creativity",
    "A timeless classic that will never go out of style",
    "A piece that reflects the latest fashion trends",
    "A unique item that stands out in any collection",
    "A piece that combines comfort and sophistication",
    "A versatile item that can be worn year-round",
    "A piece that adds a pop of color to any outfit",
    "A stylish option for both casual and formal occasions",
    "A piece that embodies the essence of modern fashion",
    "A unique blend of textures and materials for a standout look",
    "A piece that tells a story with its intricate design",
]
joins_sent = ["\n", ".\n", ". "]
joins_kv = [" ", " ", ": ", ":", " - ", "-"]

deliveries = ["Courier", "Postal service", "Parcel box", "Pick-up"]


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
    for first_name in first_names:
        for last_name in last_names:
            reviews = list(set(random.choices(users_reviews, k=random.randint(0, 20))))
            created_at = random_date(six_months_ago, today)
            customer = {
                "uid": n,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "phone": f"+48{random.randint(500000000, 799999999)}",
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": random_date(
                    datetime(1975, 1, 1), datetime(2009, 12, 31)
                ).strftime("%Y-%m-%d"),
                "country": "Poland",
                "city": random.choice(cities),
                "street": random.choice(streets),
                "street_number": random.randint(1, 200),
                "postal_code": f"{random.randint(10, 99)}-{random.randint(100, 999)}",
                "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
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

    print("Customers generated:", len(users))

    ########### ITEMS ###########

    items = []
    items_categories = defaultdict(list)

    for n in range(5_000):
        iid = n

        created_at = random_date(one_year_ago, today)
        updated_at = created_at
        expires_at = (created_at + timedelta(days=random.randint(15, 60)))

        category = random.choice(list(categories.keys()))
        table = f"items_{category}"

        items.append(
            {
                "iid": iid,
                "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "category": category,
                "table": table,
            }
        )
        

        subcategory = random.choice(list(categories[category].keys()))
        type = random.choice(types)
        condition = random.choice(condtions)
        material = random.choice(materials)
        color = random.choice(colors)
        brand = random.choice(brands)
        pattern = random.choice(patterns)

        features = {
            "condition": condition,
            "brand": brand,
            "material": material,
            "color": color,
            "pattern": pattern,
            **{
                k: random.choice(v)
                for k, v in categories[category][subcategory].items()
            },
        }
        seller = users[random.randint(0, len(users) // 3)]
        name = f"{brand} {color} {subcategory}"

        join_kv: str = random.choice(joins_kv)
        join_sent: str = random.choice(joins_sent)

        desc = list(set(random.choices(descriptions, k=random.randint(2, 6))))
        feat = list(set(random.choices(list(features.items()), k=len(desc) - 1)))
        description = []
        for d, f in zip(desc, feat):
            (description.append(d),)
            description.append(join_kv.join([str(x) for x in f]))
        description.append(desc[-1])
        description = join_sent.join(description)

        item = {
            "iid": iid,
            "seller": seller["uid"],
            "city": seller["city"],
            "street": seller["street"],
            "name": name,
            "subcategory": subcategory,
            "type": type,
            "interested": random.randint(0, 30),
            "images": [],
            "description": description,
            "delivery": list(set(random.choices(
                deliveries, k=random.randint(1, len(deliveries))
            ))),
            "seller_rating": seller["rating"],
            **features
        }

        items_categories[table].append(item)

    with open(filepath_items, "w") as file:
        json.dump(items, file, indent=4)

    for table, items_list in items_categories.items():
        filepath = os.path.join(dir_files_db, f"{table}.json")
        with open(filepath, "w") as file:
            json.dump(items_list, file, indent=4)

    print("Items generated:", len(items))

    ########### TRANSACTIONS ###########
    transactions = []
    for n in range(4_000):
        item: dict = items.pop()
        item_details = items_categories[item["table"]].pop()

        while True:
            customer_id = random.choice(users)["uid"]
            if customer_id != item_details["seller"]:
                break

        transaction_date = random_date(
            datetime.fromisoformat(item["created_at"]),
            datetime.fromisoformat(item["expires_at"]),
        )

        transaction = {
            "tid": n,
            "iid": item_details["iid"],
            "name": item_details["name"],
            "seller": item_details["seller"],
            "date": transaction_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "buyer": customer_id,
            "item": item_details,
        }
        transactions.append(transaction)

    with open(filepath_transactions, "w") as file:
        json.dump(transactions, file, indent=4)

    print("Transactions generated:", len(transactions))


if __name__ == "__main__":
    main()
