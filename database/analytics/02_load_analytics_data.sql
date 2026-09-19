-- =========================================================
-- RESET ANALYTICS LAYER
-- =========================================================

TRUNCATE TABLE
    analytics.fact_sales,
    analytics.fact_order_processing,
    analytics.dim_customer,
    analytics.dim_product,
    analytics.dim_seller,
    analytics.dim_date
RESTART IDENTITY
CASCADE;


-- =========================================================
-- LOAD DATE DIMENSION
-- =========================================================

INSERT INTO analytics.dim_date (
    date_key,
    full_date,
    day,
    month,
    month_name,
    month_short_name,
    quarter,
    year,
    year_month
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d,
    EXTRACT(DAY FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    TO_CHAR(d, 'FMMonth'),
    TO_CHAR(d, 'Mon'),
    EXTRACT(QUARTER FROM d)::INTEGER,
    EXTRACT(YEAR FROM d)::INTEGER,
    TO_CHAR(d, 'YYYY-MM')
FROM GENERATE_SERIES(
    (SELECT MIN(order_date) FROM orders),
    (SELECT MAX(order_date) FROM orders),
    INTERVAL '1 day'
) AS dates(d);


-- =========================================================
-- LOAD CUSTOMER DIMENSION
-- =========================================================

INSERT INTO analytics.dim_customer (
    customer_code,
    customer_name,
    tax_id,
    region,
    credit_limit,
    active
)
SELECT
    customer_code,
    customer_name,
    tax_id,
    region,
    credit_limit,
    active
FROM customers
ORDER BY customer_code;


-- =========================================================
-- LOAD PRODUCT DIMENSION
-- =========================================================

INSERT INTO analytics.dim_product (
    product_code,
    product_description,
    category,
    brand,
    units_per_case,
    active
)
SELECT
    product_code,
    description,
    category,
    brand,
    units_per_case,
    active
FROM products
ORDER BY product_code;


-- =========================================================
-- LOAD SELLER DIMENSION
-- =========================================================

INSERT INTO analytics.dim_seller (
    seller_id,
    seller_code,
    seller_name,
    region
)
SELECT
    seller_id,
    seller_code,
    seller_name,
    region
FROM sellers
ORDER BY seller_id;


-- =========================================================
-- LOAD SALES FACT
--
-- Grain:
-- one item belonging to one APPROVED order
-- =========================================================

INSERT INTO analytics.fact_sales (
    date_key,
    customer_key,
    product_key,
    seller_key,
    order_id,
    order_item_id,
    purchase_order,
    quantity,
    unit_price,
    sales_amount
)
SELECT
    TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER,

    dc.customer_key,

    dp.product_key,

    ds.seller_key,

    o.order_id,

    oi.order_item_id,

    o.purchase_order,

    oi.quantity,

    oi.unit_price,

    oi.line_total

FROM orders o

INNER JOIN order_items oi
    ON oi.order_id = o.order_id

INNER JOIN analytics.dim_customer dc
    ON dc.customer_code = o.customer_code

INNER JOIN analytics.dim_product dp
    ON dp.product_code = oi.product_code

LEFT JOIN analytics.dim_seller ds
    ON ds.seller_id = o.seller_id

WHERE o.status = 'APPROVED';


-- =========================================================
-- LOAD ORDER PROCESSING FACT
--
-- Grain:
-- one processed order record
-- =========================================================

INSERT INTO analytics.fact_order_processing (
    date_key,
    customer_key,
    seller_key,
    order_id,
    purchase_order,
    order_status,
    processed_orders,
    approved_orders,
    rejected_orders,
    order_amount,
    error_count
)
SELECT
    TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER,

    dc.customer_key,

    ds.seller_key,

    o.order_id,

    o.purchase_order,

    o.status,

    1,

    CASE
        WHEN o.status = 'APPROVED'
        THEN 1
        ELSE 0
    END,

    CASE
        WHEN o.status = 'REJECTED'
        THEN 1
        ELSE 0
    END,

    o.total_amount,

    COALESCE(
        errors.error_count,
        0
    )

FROM orders o

LEFT JOIN analytics.dim_customer dc
    ON dc.customer_code = o.customer_code

LEFT JOIN analytics.dim_seller ds
    ON ds.seller_id = o.seller_id

LEFT JOIN (
    SELECT
        order_id,
        COUNT(*) AS error_count
    FROM processing_errors
    GROUP BY order_id
) errors
    ON errors.order_id = o.order_id;