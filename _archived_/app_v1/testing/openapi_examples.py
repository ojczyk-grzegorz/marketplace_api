EXAMPLE_CREATE_ITEM = {
    "single": {
        "summary": "single item example",
        "value": {
            "name": "4K Ultra HD Smart TV (55-inch)",
            "prices": [
                {
                    "date": "2025-09-21",
                    "price": 799.99,
                }
            ],
            "category": "Home Entertainment",
            "brand": "VisionView",
            "rating": 4.7,
        },
    },
    "multiple": {
        "summary": "multiple items example",
        "value": [
            {
                "name": "Robot Vacuum Cleaner with Mopping",
                "prices": [
                    {
                        "date": "2025-09-21",
                        "price": 299.99,
                    }
                ],
                "category": "Smart Home Appliances",
                "brand": "CleanBot",
                "rating": 4.3,
            },
            {
                "name": "Noise-Cancelling Bluetooth Headphones",
                "prices": [
                    {
                        "date": "2025-09-21",
                        "price": 149.99,
                    }
                ],
                "category": "Audio",
                "brand": "SoundScape",
                "rating": 4.5,
            },
        ],
    },
    "lacking": {
        "summary": "lacking item example",
        "value": {"name": "4K Ultra HD Smart TV (55-inch)"},
    },
    "error": {
        "summary": "error - no name",
        "value": {
            "prices": [
                {
                    "date": "2025-09-21",
                    "price": 149.99,
                }
            ],
            "category": "Audio",
            "brand": "SoundScape",
            "rating": 4.5,
        },
    },
}


EXAMPLE_UPDATE_ITEM = {
    "single_details": {
        "value": [
            {
                "prices": [
                    {
                        "date": "2025-09-21",
                        "price": 499.99,
                    }
                ],
                "rating": 4.8,
                "iid": 1,
            }
        ]
    },
    "multiple_details": {
        "value": [
            {
                "prices": [
                    {
                        "date": "2025-09-21",
                        "price": 299.99,
                    }
                ],
                "rating": 4.2,
                "iid": 2,
            },
            {
                "prices": [
                    {
                        "date": "2025-09-21",
                        "price": 199.99,
                    }
                ],
                "rating": 4.3,
                "iid": 3,
            },
        ],
    },
    "single_stocks": {
        "value": [
            {
                "shipments": [
                    {
                        "date": "2025-09-21",
                        "quantity": 24,
                        "status": "In Transit",
                        "destination": "Store A",
                    },
                ],
                "iid": 1,
            }
        ],
    },
    "multiple_stocks": {
        "value": [
            {
                "shipments": [
                    {
                        "date": "2025-08-12",
                        "quantity": 33,
                        "status": "In Transit",
                        "destination": "Store B",
                    },
                ],
                "iid": 2,
            },
            {
                "shipments": [
                    {
                        "date": "2025-07-13",
                        "quantity": 55,
                        "status": "In Transit",
                        "destination": "Store C",
                    },
                ],
                "iid": 3,
            },
        ],
    },
}


EXAMPLE_CREATE_CUSTOMER = {
    "single": {
        "summary": "single customer example",
        "value": [
            {
                "first_name": "Elbertina",
                "last_name": "Jandac",
                "email": "ejandac0002@utexas.edu",
                "company": "Mitchell-Pfannerstill",
                "country": "China",
                "city": "Pingkai",
                "street_name": "Butternut",
                "street_number": "25",
                "postal_code": None,
            }
        ],
    },
    "multiple": {
        "summary": "multiple customers example",
        "value": [
            {
                "first_name": "Ernesta",
                "last_name": "Fischer",
                "email": "efischer1003@4shared.com",
                "company": "Reichert-Spinka",
                "country": "Indonesia",
                "city": "Panghadangan",
                "street_name": "Bartelt",
                "street_number": "1",
                "postal_code": None,
            },
            {
                "first_name": "Ty",
                "last_name": "Dutchburn",
                "email": "tdutchburn2003@ameblo.jp",
                "company": "Lubowitz, Langworth and Predovic",
                "country": "Japan",
                "city": "Nanao",
                "street_name": "Vera",
                "street_number": "2354",
                "postal_code": "926-0867",
            },
        ],
    },
    "lacking": {
        "summary": "lacking customer example",
        "value": [
            {
                "last_name": "Dutchburn",
                "email": "tdutchburn2004@ameblo.jp",
            }
        ],
    },
    "error": {
        "summary": "error - email used already",
        "value": [
            {
                "first_name": "Elbertina",
                "last_name": "Jandac",
                "email": "ejandac0@utexas.edu",
                "company": "Mitchell-Pfannerstill",
                "country": "China",
                "city": "Pingkai",
                "street_name": "Butternut",
                "street_number": "25",
                "postal_code": None,
            }
        ],
    },
}


EXAMPLE_UPDATE_CUSTOMER = {
    "single_details": {
        "value": [
            {
                "first_name": "Elbertinaaaaaa",
                "last_name": "Jandacccccc",
                "uid": 1,
            }
        ],
    },
    "multiple_details": {
        "value": [
            {
                "first_name": "Ernestaaaaa",
                "last_name": "Fischerrrrrr",
                "uid": 2,
            },
            {
                "first_name": "Tyyyyyyyy",
                "last_name": "Dutchburnnnnnnnnn",
                "uid": 3,
            },
        ],
    },
    "error": {
        "value": [
            {
                "first_name": "Elbertinaaaaa",
                "last_name": "Jandaccccc",
            }
        ],
    },
}


EXAMPLE_CREATE_TRANSACTION = {
    "multiple_details": {
        "value": [
            {
                "uid": 2,
                "iid": 2,
                "quantity": 2,
            },
            {
                "uid": 3,
                "iid": 3,
                "quantity": 3,
            },
        ],
    },
    "error": {
        "value": [
            {
                "uid": 4,
                "iid": 4,
                "quantity": 1_000_000,  # Exceeds available stock
            },
        ],
    },
}
