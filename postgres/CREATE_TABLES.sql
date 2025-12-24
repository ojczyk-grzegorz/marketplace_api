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
    brand VARCHAR(128),
    description TEXT,
    features JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    stock INT NOT NULL CONSTRAINT stock_non_negative CHECK (stock >= 0)
);


DROP TABLE IF EXISTS items_snapshots CASCADE;
CREATE TABLE items_snapshots (
	item_id UUID NOT NULL,
    name VARCHAR(256) NOT NULL,    
    category VARCHAR(32),
    subcategories VARCHAR(32)[],
    price NUMERIC NOT NULL,
    brand VARCHAR(128),
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


DROP TABLE IF EXISTS delivery_options CASCADE;
CREATE TABLE delivery_options (
    option_id UUID PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    contractor_id UUID NOT NULL,
    price NUMERIC NOT NULL,

    FOREIGN KEY (contractor_id) REFERENCES ground_staff(staff_id)
);

DROP TABLE IF EXISTS discounts CASCADE;
CREATE TABLE discounts (
    discount_code VARCHAR(128) PRIMARY KEY,
    description TEXT,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ NOT NULL,
    discount_percentage NUMERIC NOT NULL,
    item_ids UUID[],
    brands VARCHAR(128)[],
    categories JSONB 
);


DROP TABLE IF EXISTS transactions CASCADE;
CREATE TABLE transactions (
	transaction_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    delivery_option_id UUID NOT NULL,
    total_price NUMERIC NOT NULL,
    name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    email VARCHAR(256) NOT NULL,
    phone VARCHAR(16) NOT NULL,
    country VARCHAR(128) NOT NULL,
    city VARCHAR(128) NOT NULL,
    postal_code VARCHAR(16) NOT NULL,
    address_line_1 VARCHAR(256) NOT NULL,
    address_line_2 VARCHAR(256),

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (delivery_option_id) REFERENCES delivery_options(option_id)
);

DROP TABLE IF EXISTS transaction_discounts CASCADE;
CREATE TABLE transaction_discounts (
    row_id SERIAL PRIMARY KEY,
	transaction_id UUID NOT NULL,
    discount_code VARCHAR(128) NOT NULL,
    
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (discount_code) REFERENCES discounts(discount_code)
);

DROP TABLE IF EXISTS transaction_items CASCADE;
CREATE TABLE transaction_items (
    row_id SERIAL PRIMARY KEY,
	transaction_id UUID NOT NULL,
    item_id UUID NOT NULL,
    item_updated_at TIMESTAMPTZ NOT NULL,
    count INT NOT NULL,
    price_after_discounts NUMERIC NOT NULL,

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
    name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    email VARCHAR(256) NOT NULL,
    phone VARCHAR(16) NOT NULL,
    country VARCHAR(128) NOT NULL,
    city VARCHAR(128) NOT NULL,
    postal_code VARCHAR(16) NOT NULL,
    address_line_1 VARCHAR(256) NOT NULL,
    address_line_2 VARCHAR(256),
    items JSONB NOT NULL,
    action_history JSONB NOT NULL
);