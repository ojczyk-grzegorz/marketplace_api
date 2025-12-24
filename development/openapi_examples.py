def get_user_create_examples() -> dict:
    return {
        "valid_request": {
            "value": {
                "email": "user2@example.com",
                "phone": "+48234567891",
                "password": "p2",
            },
        },
        "invalid_email": {
            "value": {
                "email": "user3example.com",
                "phone": "+48234567891",
                "password": "p2",
            },
        },
        "user_exists": {
            "value": {
                "email": "user@example.com",
                "phone": "+48123456789",
                "password": "p2",
            },
        }
    }


def get_user_update_examples() -> dict:
    return {
        "valid_request": {
            "value": {
                "email": "user3@example.com",
                "phone": "+48345678912",
                "password": "p3",
            },
        },
        "invalid_email": {
            "value": {
                "email": "user3example.com",
                "phone": "+48234567891",
                "password": "p2",
            },
        },
    }


def get_filter_items_examples() -> dict:
    return {
        "valid_apple_1": {
            "value": {
                "search": "apple",
            },
        },
        "valid_apple_2": {
            "value": {
                "search": "Apple",
            },
        },
        "valid_3": {
            "value": {
                "category": "Electronics",
                "price": [500, 1500],
            },
        },
    }


def get_retrieve_item_examples() -> dict:
    return {
        "valid_request": {
            "value": "550e8400-e29b-41d4-a716-446655440001",
        },
        "invalid_request": {
            "value": "00000000-0000-0000-0000-000000000000",
        },
    }



def get_transaction_create_examples() -> dict:
    return {
        "valid_request": {
            "value": {
                "item_ids": {
                    "550e8400-e29b-41d4-a716-446655440001": 1,
                    "550e8400-e29b-41d4-a716-446655440003": 1,
                },
                "delivery_option_id": "13f92f95-5fe7-46b5-8893-5ea1a5eeae5a",
                "discount_codes": ["APPLE_SALE", "ELECTRONICS_LAPTOPS_SALE"],
                "name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "phone": "+48123456789",
                "country": "Poland",
                "city": "Kraków",
                "postal_code": "31-001",
                "address_line_1": "Wawel Cathedral, Wawel",
            },
        },
        "invalid_item_request": {
            "value": {
                "item_ids": {
                    "00000000-0000-0000-0000-000000000000": 1,
                },
                "delivery_option_id": "13f92f95-5fe7-46b5-8893-5ea1a5eeae5a",
                "discount_codes": ["APPLE_SALE", "ELECTRONICS_LAPTOPS_SALE"],
                "name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "phone": "+48123456789",
                "country": "Poland",
                "city": "Kraków",
                "postal_code": "31-001",
                "address_line_1": "Wawel Cathedral, Wawel",
            },
        },
        "invalid_delivery_request": {
            "value": {
                "item_ids": {
                    "550e8400-e29b-41d4-a716-446655440001": 1,
                    "550e8400-e29b-41d4-a716-446655440003": 1,
                },
                "delivery_option_id": "00000000-0000-0000-0000-000000000000",
                "discount_codes": ["APPLE_SALE", "ELECTRONICS_LAPTOPS_SALE"],
                "name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "phone": "+48123456789",
                "country": "Poland",
                "city": "Kraków",
                "postal_code": "31-001",
                "address_line_1": "Wawel Cathedral, Wawel",
            },
        },
    }
