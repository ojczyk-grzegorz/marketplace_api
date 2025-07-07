USER_CREATE = {
    "good": {
        "value": {
            "email": "adam.piotrowski@example.com",
            "phone": "+48708315166",
            "password": "password",
            "first_name": "Adam",
            "last_name": "Piotrowski",
            "birth_date": "2008-07-29",
            "country": "PL",
            "city": "Radom",
            "street": "Holenderska",
            "street_number": "21",
            "postal_code": "10-708",
        }
    },
    "bad": {
        "value": {
            "email": "adam.baran@example.com",
            "phone": "+48725792650",
            "password": "password",
            "first_name": "Adam",
            "last_name": "Baran",
            "country": "PL",
            "city": "Lublin",
            "created_at": "2025-03-21T00:00:00Z",
            "updated_at": "2025-03-21T00:00:00Z",
            "birth_date": "1976-10-25",
            "street": "Słoweńska",
            "street_number": "125",
            "postal_code": "61-902",
        }
    },
}


USER_PATCH = {
    "good": {
        "value": {
            "email": "adam.sadowski@example.com",
            "phone": "+48679530542",
            "first_name": "Adam",
            "last_name": "Sadowski",
            "birth_date": "1982-03-07",
            "country": "PL",
            "city": "Bydgoszcz",
            "street": "Hiszpa\u0144ska",
            "street_number": "164",
            "postal_code": "67-487",
        }
    }
}
