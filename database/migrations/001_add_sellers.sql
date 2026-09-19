CREATE TABLE IF NOT EXISTS sellers (
    seller_id INTEGER PRIMARY KEY,
    seller_code VARCHAR(20) NOT NULL UNIQUE,
    seller_name VARCHAR(150) NOT NULL,
    region VARCHAR(50)
);