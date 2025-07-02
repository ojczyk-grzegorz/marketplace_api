import datetime as dt

ITEM_CREATE = {
    "single": {
        "summary": "single item example",
        "value": {
            "name": "Evergreen & Elm Blue Rubber Sneakers",
            "seller_id": 6,
            "price": 288.0,
            "brand": "Evergreen & Elm",
            "category": "Sneakers",
            "material": "Rubber",
            "color": "Blue",
            "type": "Fashion",
            "style": "Fashion",
            "condition": "Poor",
            "pattern": "Geometric",
            "size": 53.0,
            "width": "Regular",
            "fastener": "Laces",
            "heel": "Wedge",
            "toe": "Almond",
            "country": "PL",
            "city": "Lublin",
            "expires_at": dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30),
            "icon": None,
            "images": [],
            "description": "A versatile item that can be styled in multiple ways. toe Almond. A fusion of traditional and modern styles. width Regular. Crafted with high-quality materials for durability",
        },
    },
}

ITEM_PATCH = {
    "single": {
        "summary": "single item example",
        "value": {
            "iid": 10,
            "name": "Phantom Fit Navy Synthetic Loafers",
            "price": 297.0,
            "brand": "Phantom Fit",
            "category": "Loafers",
            "material": "Synthetic",
            "color": "Navy",
            "type": "Formal",
            "style": "Running",
            "condition": "Good",
            "pattern": "Geometric",
            "size": 60.0,
            "width": "Wide",
            "fastener": "Zipper",
            "heel": "Wedge",
            "toe": "Open",
            "country": "PL",
            "city": "Toru\u0144",
            "expires_at": dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30),
            "icon": None,
            "images": [],
            "description": "A piece that brings a touch of elegance to any outfit\nwidth: Wide\nA timeless classic that will never go out of style\ntoe: Open\nA unique item that stands out in any collection\npattern: Geometric\nIdeal for layering or wearing on its own",
        },
    },
}

ITEM_DELETE = {
    "single": {
        "summary": "single item example",
        "value": {"item_id": 10},
    },
}
