CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    uid SERIAL PRIMARY KEY,
    uid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    phone VARCHAR(16) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
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

    description TEXT,

    FOREIGN KEY (seller_id) REFERENCES users(uid)
);


DROP TABLE IF EXISTS transactions CASCADE;
CREATE TABLE transactions (
	tid SERIAL PRIMARY KEY,
	tid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    sold_at TIMESTAMPTZ NOT NULL,
    item JSONB,
    seller_uid_uuid4 UUID NOT NULL,
    buyer_uid_uuid4 UUID NOT NULL,
    seller_snapshot JSONB,
    buyer_snapshot JSONB,
    finilized TIMESTAMPTZ DEFAULT NULL
);


DROP TABLE IF EXISTS logs_request CASCADE;
CREATE TABLE logs_request (
	rid_uuid4 UUID UNIQUE NOT NULL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    url TEXT NOT NULL,
    method VARCHAR(8) NOT NULL,
    status_code INT NOT NULL,
    duration_ms NUMERIC NOT NULL,
    type VARCHAR(16) NOT NULL,
    http_version VARCHAR(8) NOT NULL,
    server JSONB,
    client JSONB,
    path TEXT NOT NULL,
    path_params JSONB,
    asgi_version VARCHAR(16) NOT NULL,
    asgi_spec_version VARCHAR(16) NOT NULL,
    request_headers JSONB,
    request_body JSONB,
    response_headers JSONB,
    response_body JSONB,
    exception JSONB
);


DROP TABLE IF EXISTS logs_query CASCADE;
CREATE TABLE logs_query (
	lid SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    duration_ms NUMERIC NOT NULL,
    query_details JSONB
);