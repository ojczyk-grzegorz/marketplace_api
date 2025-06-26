CREATE DATABASE marketplace_api
	WITH 
	OWNER = postgres
	ENCODING = 'UTF-8'
	LOCALE_PROVIDER = 'libc'
	CONNECTION LIMIT = -1
	IS_TEMPLATE = False;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
	
	
-- SELECT * FROM pg_timezone_names;
ALTER DATABASE marketplace_api
	SET timezone TO 'UTC';


CREATE TABLE users (
    uid SERIAL PRIMARY KEY,
    uid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(256) NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    phone VARCHAR(16) UNIQUE NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    birth_date DATE NOT NULL,
    country VARCHAR(4) NOT NULL,
    city VARCHAR(128) NOT NULL,
    street VARCHAR(128) NOT NULL,
    street_number VARCHAR(16) NOT NULL,
    postal_code VARCHAR(16) NOT NULL,
    addresses JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ NOT NULL,
    reviews JSONB,
    rating DECIMAL(1,2) NOT NULL DEFAULT 0.0,
    avatar TEXT
);


ALTER TABLE users
	ADD CONSTRAINT unique_id
	UNIQUE (uid_uuid4);


CREATE TABLE categories (
    cid SERIAL PRIMARY KEY,
    name VARCHAR(256) NOT NULL
);


ALTER TABLE categories
    ADD CONSTRAINT unique_category_name
    UNIQUE (name);


CREATE TABLE status (
    sid SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL UNIQUE
);


CREATE TABLE transactions (
    tid SERIAL PRIMARY KEY,
    tid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    buyer_id  INT NOT NULL,
    status_id INT NOT NULL,
    transaction_start TIMESTAMPTZ NOT NULL,
    transaction_end TIMESTAMPTZ,
    
    FOREIGN KEY (buyer_id) REFERENCES users(uid),
    FOREIGN KEY (status_id) REFERENCES status(sid),
);


CREATE TABLE items (
	iid SERIAL PRIMARY KEY,
	iid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(256) NOT NULL,
    cid INT NOT NULL,
    seller_id INT NOT NULL,
    seller_rating DECIMAL(1,2) NOT NULL DEFAULT 0.0,
    transaction_id INT NOT NULL,
    subcategory VARCHAR(32) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    condition VARCHAR(32) NOT NULL,
    brand VARCHAR(64),
    material VARCHAR(32),
    color VARCHAR(16),
    pattern VARCHAR(32),
    size VARCHAR(16),
    style VARCHAR(32),
    features_specific JSONB,
    city VARCHAR(128) NOT NULL,
    street VARCHAR(128) NOT NULL,
    delivery JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    icon TEXT,
    images JSONB,
    interested INTEGER DEFAULT 0,
    description TEXT,

    FOREIGN KEY (cid) REFERENCES categories(cid),
    FOREIGN KEY (seller_id) REFERENCES users(uid),
    FOREIGN KEY (transaction_id) REFERENCES transactions(tid)
);