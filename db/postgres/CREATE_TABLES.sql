CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS transactions_active CASCADE;
DROP TABLE IF EXISTS transcations_archived CASCADE;

DROP TABLE IF EXISTS items CASCADE;

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
    addresses JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ NOT NULL,
    reviews JSONB,
    rating NUMERIC NOT NULL DEFAULT 0.0,
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


CREATE TABLE transactions_active (
    tid SERIAL PRIMARY KEY,
    tid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    buyer_id  INT NOT NULL,
    status_id INT NOT NULL,
    transaction_start TIMESTAMPTZ NOT NULL,
    transaction_end TIMESTAMPTZ,
    
    FOREIGN KEY (buyer_id) REFERENCES users(uid),
    FOREIGN KEY (status_id) REFERENCES status(sid)
);


CREATE TABLE items (
	iid SERIAL PRIMARY KEY,
	iid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(256) NOT NULL,
    category_id INT NOT NULL,
    seller_id INT NOT NULL,
    seller_rating NUMERIC NOT NULL DEFAULT 0.0,
    transaction_id INT,
    subcategory VARCHAR(32) NOT NULL,
    price NUMERIC NOT NULL,
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

    FOREIGN KEY (category_id) REFERENCES categories(cid),
    FOREIGN KEY (seller_id) REFERENCES users(uid),
    FOREIGN KEY (transaction_id) REFERENCES transactions_active(tid)
);


CREATE TABLE transcations_archived (
    tid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    status VARCHAR(32) NOT NULL,
    transaction_start TIMESTAMPTZ NOT NULL,
    transaction_end TIMESTAMPTZ NOT NULL,
    item_id_uuid4 UUID NOT NULL,
    item_snapshot JSONB NOT NULL,
    buyer_id_uuid4 UUID NOT NULL,
    buyer_snapshot JSONB NOT NULL,
    seller_id_uuid4 UUID NOT NULL,
    seller_snapshot JSONB NOT NULL
);
