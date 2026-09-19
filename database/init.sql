CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    tax_id VARCHAR(30) NOT NULL,
    region VARCHAR(50),
    seller_id INTEGER,
    credit_limit NUMERIC(14, 2),
    active BOOLEAN NOT NULL
);


CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_code VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    units_per_case INTEGER,
    unit_price NUMERIC(14, 2),
    active BOOLEAN NOT NULL
);


CREATE TABLE IF NOT EXISTS orders (
    order_id BIGSERIAL PRIMARY KEY,
    purchase_order VARCHAR(30) NOT NULL,
    order_date DATE NOT NULL,
    customer_code VARCHAR(20),
    customer_name VARCHAR(150),
    seller_id INTEGER,
    status VARCHAR(20) NOT NULL,
    total_amount NUMERIC(16, 2),
    processed_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_code VARCHAR(20),
    description VARCHAR(200),
    category VARCHAR(100),
    brand VARCHAR(100),
    quantity INTEGER,
    units_per_case INTEGER,
    unit_price NUMERIC(14, 2),
    stock_quantity INTEGER,
    line_total NUMERIC(16, 2),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS processing_errors (
    processing_error_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    order_item_id BIGINT,
    error_type VARCHAR(100) NOT NULL,
    error_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_processing_errors_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_processing_errors_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(order_item_id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_orders_purchase_order
    ON orders(purchase_order);

CREATE INDEX IF NOT EXISTS idx_orders_customer_code
    ON orders(customer_code);

CREATE INDEX IF NOT EXISTS idx_orders_order_date
    ON orders(order_date);

CREATE INDEX IF NOT EXISTS idx_order_items_product_code
    ON order_items(product_code);

CREATE INDEX IF NOT EXISTS idx_processing_errors_type
    ON processing_errors(error_type);