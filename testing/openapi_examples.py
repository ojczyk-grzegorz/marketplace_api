def get_user_create_examples():
    return {
        "example1": {
            "summary": "Example user creation payload",
            "value": {
                "email": "user2@example.com",
                "phone": "+48234567891",
                "password": "p2",
            },
        }
    }


def get_user_update_examples():
    return {
        "example1": {
            "summary": "Example user creation payload",
            "value": {
                "email": "user3@example.com",
                "phone": "+48345678912",
                "password": "p3",
            },
        }
    }


def get_transaction_create_examples():
    return {
        "example1": {
            "summary": "Example transaction creation payload",
            "value": {
                "item_ids": {
                    "550e8400-e29b-41d4-a716-446655440001": 1,
                    "550e8400-e29b-41d4-a716-446655440003": 1,
                },
                "delivery_option_id": "13f92f95-5fe7-46b5-8893-5ea1a5eeae5a",
                "discount_codes": ["APPLE_SALE", "ELECTRONICS_LAPTOPS_SALE"],
            },
        }
    }
