CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    uid SERIAL PRIMARY KEY,
    uid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    phone VARCHAR(16) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    birth_date DATE NOT NULL,
    country VARCHAR(4) NOT NULL,
    city VARCHAR(128) NOT NULL,
    street VARCHAR(128) NOT NULL,
    street_number VARCHAR(16) NOT NULL,
    postal_code VARCHAR(16) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


DROP TABLE IF EXISTS items CASCADE;
CREATE TABLE items (
	iid SERIAL PRIMARY KEY,
	iid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(256) NOT NULL,
    seller_id INT NOT NULL,
    price NUMERIC NOT NULL,
    
    category VARCHAR(32),
    type VARCHAR(32),
    style VARCHAR(32),
    brand VARCHAR(64),
    condition VARCHAR(16),
    material VARCHAR(32),
    color VARCHAR(16),
    pattern VARCHAR(32),
    size NUMERIC,
    
    width VARCHAR(32),
    fastener VARCHAR(32),
    heel VARCHAR(32),
    toe VARCHAR(32),
    
    country VARCHAR(4) NOT NULL,
    city VARCHAR(128) NOT NULL,
    
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,

    icon TEXT,
    images JSONB,
    description TEXT,

    FOREIGN KEY (seller_id) REFERENCES users(uid)
);


DROP TABLE IF EXISTS transactions CASCADE;
CREATE TABLE transactions (
	tid SERIAL PRIMARY KEY,
	tid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    sold_at TIMESTAMPTZ NOT NULL,
    item JSONB NOT NULL,
    seller_uid_uuid4 UUID NOT NULL,
    buyer_uid_uuid4 UUID NOT NULL,
    seller_snapshot JSONB NOT NULL,
    buyer_snapshot JSONB NOT NULL,
    finilized BOOLEAN NOT NULL DEFAULT FALSE
);