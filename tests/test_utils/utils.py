CONFIGS_JSON = """{
    "app_name": "app_name",
    "database": {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "password",
        "database": "database",
        "tables": {
            "users": {
                "name": "users"
            },
            "items": {
                "name": "items"
            },
            "transactions": {
                "name": "transactions"
            },
            "logs_request": {
                "name": "logs_request"
            },
            "logs_query": {
                "name": "logs_query"
            }
        }
    },
    "auth": {
        "secret_key": "SECRET",
        "algorithm": "HS256",
        "access_token_expire_minutes": 30
    }
}"""
