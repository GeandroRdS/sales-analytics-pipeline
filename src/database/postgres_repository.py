import os

import psycopg
from dotenv import load_dotenv


class PostgresRepository:
    """
    Handles persistence of processed sales orders
    in PostgreSQL.
    """

    def __init__(self):

        load_dotenv()

        self.connection_parameters = {
            "host": os.getenv(
                "POSTGRES_HOST",
                "localhost",
            ),
            "port": os.getenv(
                "POSTGRES_PORT",
                "5433",
            ),
            "dbname": os.getenv(
                "POSTGRES_DB",
                "sales_analytics",
            ),
            "user": os.getenv(
                "POSTGRES_USER",
            ),
            "password": os.getenv(
                "POSTGRES_PASSWORD",
            ),
        }

    def test_connection(self) -> None:

        with psycopg.connect(
            **self.connection_parameters
        ) as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT current_database();"
                )

                database = cursor.fetchone()[0]

                print(
                    f"PostgreSQL connection successful: "
                    f"{database}"
                )

    def replace_processing_data(
        self,
        results: list[dict],
    ) -> None:
        """
        Replaces the current processed dataset.

        This makes local development reproducible:
        running the pipeline multiple times does not
        duplicate previously loaded records.
        """

        with psycopg.connect(
            **self.connection_parameters
        ) as connection:

            try:

                with connection.cursor() as cursor:

                    self._clear_processing_tables(
                        cursor
                    )

                    self._load_master_data(
                        cursor,
                        results,
                    )

                    self._load_orders(
                        cursor,
                        results,
                    )

                connection.commit()

            except Exception:

                connection.rollback()
                raise

    def _clear_processing_tables(
        self,
        cursor,
    ) -> None:

        cursor.execute(
            """
            TRUNCATE TABLE
                processing_errors,
                order_items,
                orders,
                customers,
                products
            RESTART IDENTITY
            CASCADE;
            """
        )

    def _load_master_data(
        self,
        cursor,
        results: list[dict],
    ) -> None:

        customers = {}
        products = {}

        for result in results:

            customer = result.get(
                "customer"
            )

            if customer:

                customers[
                    customer["customer_code"]
                ] = customer

            for item in result["items"]:

                if (
                    item["unit_price"] is None
                    or item["product_code"]
                    == "PRD-9999"
                ):
                    continue

                products[
                    item["product_code"]
                ] = item

        for customer in customers.values():

            cursor.execute(
                """
                INSERT INTO customers (
                    customer_id,
                    customer_code,
                    customer_name,
                    tax_id,
                    region,
                    seller_id,
                    credit_limit,
                    active
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                );
                """,
                (
                    customer["customer_id"],
                    customer["customer_code"],
                    customer["customer_name"],
                    customer["tax_id"],
                    customer["region"],
                    customer["seller_id"],
                    customer["credit_limit"],
                    customer["active"],
                ),
            )

        product_id = 1

        for product in products.values():

            cursor.execute(
                """
                INSERT INTO products (
                    product_id,
                    product_code,
                    description,
                    category,
                    brand,
                    units_per_case,
                    unit_price,
                    active
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                );
                """,
                (
                    product_id,
                    product["product_code"],
                    product["description"],
                    product["category"],
                    product["brand"],
                    product["units_per_case"],
                    product["unit_price"],
                    "INACTIVE_PRODUCT"
                    not in product["errors"],
                ),
            )

            product_id += 1

    def _load_orders(
        self,
        cursor,
        results: list[dict],
    ) -> None:

        for result in results:

            total_amount = sum(
                item["line_total"] or 0
                for item in result["items"]
            )

            customer = (
                result.get("customer")
                or {}
            )

            seller_id = customer.get(
                "seller_id"
            )

            cursor.execute(
                """
                INSERT INTO orders (
                    purchase_order,
                    order_date,
                    customer_code,
                    customer_name,
                    seller_id,
                    status,
                    total_amount
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
                RETURNING order_id;
                """,
                (
                    result["purchase_order"],
                    result["order_date"],
                    result["customer_code"],
                    result["customer_name"],
                    seller_id,
                    result["status"],
                    total_amount,
                ),
            )

            order_id = cursor.fetchone()[0]

            item_error_types = set()

            for item in result["items"]:

                order_item_id = (
                    self._insert_order_item(
                        cursor,
                        order_id,
                        item,
                    )
                )

                for error in item["errors"]:

                    item_error_types.add(
                        error
                    )

                    self._insert_error(
                        cursor=cursor,
                        order_id=order_id,
                        order_item_id=order_item_id,
                        error_type=error,
                        error_level="ITEM",
                    )

            for error in result["errors"]:

                if error in item_error_types:
                    continue

                self._insert_error(
                    cursor=cursor,
                    order_id=order_id,
                    order_item_id=None,
                    error_type=error,
                    error_level="ORDER",
                )

    def _insert_order_item(
        self,
        cursor,
        order_id: int,
        item: dict,
    ) -> int:

        cursor.execute(
            """
            INSERT INTO order_items (
                order_id,
                product_code,
                description,
                category,
                brand,
                quantity,
                units_per_case,
                unit_price,
                stock_quantity,
                line_total
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            RETURNING order_item_id;
            """,
            (
                order_id,
                item["product_code"],
                item["description"],
                item["category"],
                item["brand"],
                item["quantity"],
                item["units_per_case"],
                item["unit_price"],
                item["stock_quantity"],
                item["line_total"],
            ),
        )

        return cursor.fetchone()[0]

    def _insert_error(
        self,
        cursor,
        order_id: int,
        order_item_id: int | None,
        error_type: str,
        error_level: str,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO processing_errors (
                order_id,
                order_item_id,
                error_type,
                error_level
            )
            VALUES (
                %s, %s, %s, %s
            );
            """,
            (
                order_id,
                order_item_id,
                error_type,
                error_level,
            ),
        )