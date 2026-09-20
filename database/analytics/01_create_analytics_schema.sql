CREATE SCHEMA IF NOT EXISTS analytics;


-- =========================================================
-- DIMENSION: DATE
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    month_short_name VARCHAR(10) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL
);


-- =========================================================
-- DIMENSION: CUSTOMER
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    tax_id VARCHAR(30),
    region VARCHAR(50),
    credit_limit NUMERIC(14, 2),
    active BOOLEAN
);


-- =========================================================
-- DIMENSION: PRODUCT
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_code VARCHAR(20) NOT NULL UNIQUE,
    product_description VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    units_per_case INTEGER,
    active BOOLEAN
);


-- =========================================================
-- DIMENSION: SELLER
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.dim_seller (
    seller_key BIGSERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL UNIQUE,
    seller_code VARCHAR(20) NOT NULL,
    seller_name VARCHAR(150) NOT NULL,
    region VARCHAR(50)
);


-- =========================================================
-- FACT: SALES
-- Grain: one approved order item
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    seller_key BIGINT,

    order_id BIGINT NOT NULL,
    order_item_id BIGINT NOT NULL,

    purchase_order VARCHAR(30) NOT NULL,

    quantity INTEGER NOT NULL,
    unit_price NUMERIC(14, 2) NOT NULL,
    sales_amount NUMERIC(16, 2) NOT NULL,

    CONSTRAINT fk_fact_sales_date
        FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_sales_product
        FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key),

    CONSTRAINT fk_fact_sales_seller
        FOREIGN KEY (seller_key)
        REFERENCES analytics.dim_seller(seller_key)
);


-- =========================================================
-- FACT: ORDER PROCESSING
-- Grain: one processed order record
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.fact_order_processing (
    processing_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    customer_key BIGINT,
    seller_key BIGINT,

    order_id BIGINT NOT NULL,
    purchase_order VARCHAR(30) NOT NULL,

    order_status VARCHAR(20) NOT NULL,

    processed_orders INTEGER NOT NULL DEFAULT 1,
    approved_orders INTEGER NOT NULL DEFAULT 0,
    rejected_orders INTEGER NOT NULL DEFAULT 0,

    order_amount NUMERIC(16, 2),
    error_count INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT fk_fact_processing_date
        FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_processing_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_processing_seller
        FOREIGN KEY (seller_key)
        REFERENCES analytics.dim_seller(seller_key)
);


-- =========================================================
-- DIMENSION: ERROR
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.dim_error (
    error_key BIGSERIAL PRIMARY KEY,
    error_type VARCHAR(100) NOT NULL,
    error_level VARCHAR(20) NOT NULL,

    CONSTRAINT uq_dim_error
        UNIQUE (error_type, error_level)
);


-- =========================================================
-- FACT: ORDER ERROR
-- Grain: one processing error occurrence
-- =========================================================

CREATE TABLE IF NOT EXISTS analytics.fact_order_error (
    order_error_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    customer_key BIGINT,
    seller_key BIGINT,
    error_key BIGINT NOT NULL,

    order_id BIGINT NOT NULL,
    order_item_id BIGINT,

    error_count INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT fk_fact_error_date
        FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_error_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_error_seller
        FOREIGN KEY (seller_key)
        REFERENCES analytics.dim_seller(seller_key),

    CONSTRAINT fk_fact_error_error
        FOREIGN KEY (error_key)
        REFERENCES analytics.dim_error(error_key)
);

-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_fact_error_date
    ON analytics.fact_order_error(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_error_customer
    ON analytics.fact_order_error(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_error_seller
    ON analytics.fact_order_error(seller_key);

CREATE INDEX IF NOT EXISTS idx_fact_error_error
    ON analytics.fact_order_error(error_key);

CREATE INDEX IF NOT EXISTS idx_fact_error_order
    ON analytics.fact_order_error(order_id);


CREATE INDEX IF NOT EXISTS idx_fact_sales_date
    ON analytics.fact_sales(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_customer
    ON analytics.fact_sales(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product
    ON analytics.fact_sales(product_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_seller
    ON analytics.fact_sales(seller_key);

CREATE INDEX IF NOT EXISTS idx_fact_processing_date
    ON analytics.fact_order_processing(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_processing_customer
    ON analytics.fact_order_processing(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_processing_seller
    ON analytics.fact_order_processing(seller_key);