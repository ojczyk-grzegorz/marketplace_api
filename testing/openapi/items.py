ITEM_CREATE = {
    "single": {
        "summary": "single item example",
        "value": {
            "seller_id": 823,
            "items": [
                {
                    "name": "Aetheria Apparel Blue T-Shirt",
                    "category_id": 1,
                    "subcategory": "T-Shirt",
                    "price": 40.99,
                    "condition": "Poor",
                    "brand": "Aetheria Apparel",
                    "material": "Polyester",
                    "color": "Blue",
                    "pattern": "Striped",
                    "size": "M",
                    "style": "Fashion",
                    "features_specific": {
                        "fit": "Loose",
                        "sleeve": "Short",
                        "collar": "Polo",
                    },
                    "city": "Gliwice",
                    "street": "Szwajcarska",
                    "delivery": ["Parcel box", "Postal service"],
                    "icon": None,
                    "images": [],
                    "description": "Made with sustainable practices in mind\nsize - M\nA versatile item that can be worn year-round",
                    "expires_at_days": 30,
                },
            ],
        },
    },
}

ITEM_PATCH = {
    "single": {
        "summary": "single item example",
        "value": {
            "iid": 1,
            "city": "Kielce",
            "street": "Francuska",
            "name": "Update test name",
            "subcategory": "Boots",
            "type": "Fashion",
            "description": "Lightweight and breathable for all-day comfort. material Leather. A versatile item that can be dressed up or down",
            "delivery": ["Courier", "Pick-up", "Postal service"],
            "condition": "New",
            "brand": "Wilde Folk Goods",
            "material": "Leather",
            "color": "Brown",
            "pattern": "Floral",
            "size": "45",
            "style": "Knee-High Boots",
            "price": 129.99,
            "expires_at_days": 25,
        },
    },
}
