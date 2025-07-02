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


DROP TABLE IF EXISTS status CASCADE;
CREATE TABLE status (
    sid SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL UNIQUE
);


DROP TABLE IF EXISTS transactions_active CASCADE;
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



DROP TABLE IF EXISTS categories CASCADE;
CREATE TABLE categories (
    cid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS types CASCADE;
CREATE TABLE types (
    tid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS styles CASCADE;
CREATE TABLE styles (
    sid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS brands CASCADE;
CREATE TABLE brands (
    bid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS conditions CASCADE;
CREATE TABLE conditions (
    cid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS materials CASCADE;
CREATE TABLE materials (
    mid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS colors CASCADE;
CREATE TABLE colors (
    cid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS patterns CASCADE;
CREATE TABLE patterns (
    pid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS widths CASCADE;
CREATE TABLE widths (
    wid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS fasteners CASCADE;
CREATE TABLE fasteners (
    fid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS heels CASCADE;
CREATE TABLE heels (
    hid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS toes CASCADE;
CREATE TABLE toes (
    tid SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE NOT NULL
);


DROP TABLE IF EXISTS items CASCADE;
CREATE TABLE items (
	iid SERIAL PRIMARY KEY,
	iid_uuid4 UUID DEFAULT uuid_generate_v4() UNIQUE,
    name VARCHAR(256) NOT NULL,
    seller_id INT NOT NULL,
    transaction_id INT DEFAULT NULL,
    price NUMERIC NOT NULL,
    
    category_id INT,
    type_id INT,
    style_id INT,
    brand_id INT,
    condition_id INT NOT NULL,
    material_id INT,
    color_id INT,
    pattern_id INT,
    size NUMERIC,
    
    width_id INT,
    fastener_id INT,
    heel_id INT,
    toe_id INT,
    
    country VARCHAR(4) NOT NULL,
    city VARCHAR(128) NOT NULL,
    
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,

    icon TEXT,
    images JSONB,
    description TEXT,

    FOREIGN KEY (seller_id) REFERENCES users(uid),
    FOREIGN KEY (transaction_id) REFERENCES transactions_active(tid),
    FOREIGN KEY (category_id) REFERENCES categories(cid),
    FOREIGN KEY (type_id) REFERENCES types(tid),
    FOREIGN KEY (style_id) REFERENCES styles(sid),
    FOREIGN KEY (brand_id) REFERENCES brands(bid),
    FOREIGN KEY (condition_id) REFERENCES conditions(cid),
    FOREIGN KEY (material_id) REFERENCES materials(mid),
    FOREIGN KEY (color_id) REFERENCES colors(cid),
    FOREIGN KEY (pattern_id) REFERENCES patterns(pid),
    FOREIGN KEY (width_id) REFERENCES widths(wid),
    FOREIGN KEY (fastener_id) REFERENCES fasteners(fid),
    FOREIGN KEY (heel_id) REFERENCES heels(hid),
    FOREIGN KEY (toe_id) REFERENCES toes(tid)
);


DROP TABLE IF EXISTS transactions_archived CASCADE;
CREATE TABLE transactions_archived (
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
