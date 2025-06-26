CREATE DATABASE marketplace_api
	WITH 
	OWNER = postgres
	ENCODING = 'UTF-8'
	LOCALE_PROVIDER = 'libc'
	CONNECTION LIMIT = -1
	IS_TEMPLATE = False;
	
	
-- SELECT * FROM pg_timezone_names;
ALTER DATABASE marketplace_api
	SET timezone TO 'UTC';

CREATE TABLE users (
        uid SERIAL PRIMARY KEY,
        uid_uuid4 VARCHAR(32),
        email VARCHAR(256),
        password_hash VARCHAR(64),
        phone VARCHAR(16),
        first_name VARCHAR(128),
        last_name VARCHAR(256),
        birth_date DATE,
        country VARCHAR(4),
        city VARCHAR(128),
        street VARCHAR(128),
        street_number VARCHAR(16),
        postal_code VARCHAR(16),
        created_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ,
        last_activity TIMESTAMPTZ,
        reviews JSONB,
        rating REAL,
        avatar TEXT
);

ALTER TABLE users
	ADD CONSTRAINT unique_id
	UNIQUE (uid_uuid4);



CREATE TABLE items (
	iid SERIAL PRIMARY KEY,
	iid_uuid4 VARCHAR(32) UNIQUE,
        "name": "Luminary Loft Pink Trousers",
        "cid": 0,
        "seller_id": 1020,
        "seller_rating": 3.9,
        "transaction_id": 1,
        "subcategory": "Trousers",
        "price": 25.99,
        "condition": "Not Used",
        "brand": "Luminary Loft",
        "material": "Wool",
        "color": "Pink",
        "pattern": "Denim",
        "size": "M",
        "style": "Casual",
        "features_specific": {
            "length": "Long",
            "fit": "Regular",
            "shape": "Skinny",
            "raise": "Mid"
        },
        "city": "Rybnik",
        "street": "Br\u0105zowa",
        "delivery": [
            "Postal service"
        ],
        "created_at": "2024-11-08T00:00:00",
        "updated_at": "2024-11-08T00:00:00",
        "expires_at": "2024-12-02T00:00:00",
        "icon": null,
        "images": [],
        "interested": 18,
        "description": "A piece that adds a pop of color to any outfit. fit: Regular. Lightweight and breathable for all-day comfort. shape: Skinny. Features unique details that set it apart from the rest. size: M. A piece that reflects the latest fashion trends"
)