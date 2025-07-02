USER_CREATE = {
    "good": {
        "value": {
            "email": "jakub15.nowak@example.com",
            "password_hash": "password123",
            "phone": "+48999999999",
            "first_name": "Jakub",
            "last_name": "Nowak",
            "birth_date": "1998-11-21",
            "country": "PL",
            "city": "Ruda \u015al\u0105ska",
            "street": "W\u0142oska",
            "street_number": "38",
            "postal_code": "49-201",
        }
    },
    "bad": {
        "value": {
            "email": "jakub.nowak@example.com",
            "password_hash": "password123",
            "phone": "+48999999999",
            "first_name": "Jakub",
            "last_name": "Nowak",
            "birth_date": "1998-11-21",
            "country": "PL",
            "city": "Ruda \u015al\u0105ska",
            "street": "W\u0142oska",
            "street_number": "38",
            "postal_code": "49-201",
        }
    },
}


USER_PATCH = {
    "good": {
        "value": {
            "email": "jakub22.nowak@example.com",
            "phone": "+48634489566",
            "first_name": "Jakub",
            "last_name": "Nowak",
            "birth_date": "1998-11-21",
            "country": "PL",
            "city": "Ruda \u015al\u0105ska",
            "street": "W\u0142oska",
            "street_number": "38",
            "postal_code": "49-201",
        }
    }
}
