CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    phone VARCHAR(16) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


DROP TABLE IF EXISTS items CASCADE;
CREATE TABLE items (
	item_id UUID PRIMARY KEY,
    name VARCHAR(256) NOT NULL,    
    category VARCHAR(32) NOT NULL,
    subcategories VARCHAR(32)[],
    price NUMERIC NOT NULL,
    brand VARCHAR(64),
    description TEXT,
    features JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


DROP TABLE IF EXISTS items_snapshots CASCADE;
CREATE TABLE items_snapshots (
	item_id UUID NOT NULL,
    name VARCHAR(256) NOT NULL,    
    category VARCHAR(32),
    subcategories VARCHAR(32),
    price NUMERIC NOT NULL,
    brand VARCHAR(64),
    description TEXT,
    features JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    
    PRIMARY KEY (item_id, updated_at) 
);


DROP TABLE IF EXISTS ground_staff CASCADE;
CREATE TABLE ground_staff (
    staff_id UUID PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    role VARCHAR(64) NOT NULL
);


DROP TABLE IF EXISTS transactions CASCADE;
CREATE TABLE transactions (
	transaction_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    delivery_option VARCHAR(32) NOT NULL,
    delivery_price NUMERIC NOT NULL,
    transaction_details JSONB NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS transaction_items CASCADE;
CREATE TABLE transaction_items (
	transaction_id UUID NOT NULL,
    item_id UUID NOT NULL,
    item_updated_at TIMESTAMPTZ NOT NULL,
    discount_amount NUMERIC,
    discount_code VARCHAR(64),

    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id, item_updated_at)  REFERENCES items_snapshots(item_id, updated_at)
);


DROP TABLE IF EXISTS transaction_actions CASCADE;
CREATE TABLE transaction_actions (
	action_id UUID PRIMARY KEY,
    transaction_id UUID NOT NULL,
    action VARCHAR(64) NOT NULL,
    description TEXT,
    performed_by UUID NOT NULL,
    performed_at TIMESTAMPTZ NOT NULL,

    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES ground_staff(staff_id)
);


DROP TABLE IF EXISTS transactions_finalized CASCADE;
CREATE TABLE transactions_finalized (
	transaction_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    finalized_at TIMESTAMPTZ NOT NULL,
    delivery_option VARCHAR(32) NOT NULL,
    delivery_price NUMERIC NOT NULL,
    transaction_details JSONB NOT NULL,
    items JSONB NOT NULL,
    action_history JSONB NOT NULL
);