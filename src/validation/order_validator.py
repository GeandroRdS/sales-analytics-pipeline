from integration.erp_client import ERPClient
from data.product_master import ProductMaster


class OrderValidator:
    """
    Validates parsed purchase orders using product master
    information and ERP operational data.
    """

    def __init__(
        self,
        erp_client: ERPClient,
        product_master: ProductMaster,
    ):
        self.erp = erp_client
        self.product_master = product_master

        self.processed_purchase_orders = set()

    def validate_orders(
        self,
        orders: list[dict],
    ) -> list[dict]:

        results = []

        for order in orders:
            result = self.validate_order(order)
            results.append(result)

        return results

    def validate_order(
        self,
        order: dict,
    ) -> dict:

        order_errors = []

        purchase_order = order["purchase_order"]

        # ----------------------------------------------------
        # DUPLICATE ORDER
        # ----------------------------------------------------

        if purchase_order in self.processed_purchase_orders:
            order_errors.append(
                "DUPLICATE_ORDER"
            )
        else:
            self.processed_purchase_orders.add(
                purchase_order
            )

        # ----------------------------------------------------
        # CUSTOMER
        # ----------------------------------------------------

        customer = self.erp.get_customer(
            order["customer_code"]
        )

        if customer is None:

            order_errors.append(
                "CUSTOMER_NOT_FOUND"
            )

        elif not customer["active"]:

            order_errors.append(
                "INACTIVE_CUSTOMER"
            )

        # ----------------------------------------------------
        # ITEMS
        # ----------------------------------------------------

        validated_items = []

        for item in order["items"]:

            validated_item = self._validate_item(
                item
            )

            validated_items.append(
                validated_item
            )

            order_errors.extend(
                validated_item["errors"]
            )

        # Remove repeated error types
        order_errors = list(
            dict.fromkeys(order_errors)
        )

        status = (
            "APPROVED"
            if not order_errors
            else "REJECTED"
        )

        # ----------------------------------------------------
        # SELLER
        # ----------------------------------------------------

        seller = None

        if customer:
            seller = customer.get("seller")

        return {
            "purchase_order": purchase_order,
            "order_date": order["order_date"],
            "customer_code": order["customer_code"],
            "customer_name": order["customer_name"],
            "customer": customer,
            "seller": seller,
            "status": status,
            "errors": order_errors,
            "items": validated_items,
        }

    def _validate_item(
        self,
        item: dict,
    ) -> dict:

        errors = []

        product_code = item["product_code"]
        quantity = item["quantity"]

        # ----------------------------------------------------
        # PRODUCT MASTER
        # ----------------------------------------------------

        master_product = (
            self.product_master.get_product(
                product_code
            )
        )

        # ----------------------------------------------------
        # ERP PRODUCT
        # ----------------------------------------------------

        erp_product = self.erp.get_product(
            product_code
        )

        if (
            master_product is None
            or erp_product is None
        ):
            errors.append(
                "PRODUCT_NOT_FOUND"
            )

            return {
                **item,
                "category": None,
                "brand": None,
                "units_per_case": None,
                "unit_price": None,
                "stock_quantity": None,
                "line_total": None,
                "errors": errors,
            }

        # ----------------------------------------------------
        # PRODUCT STATUS
        # ----------------------------------------------------

        if not erp_product["active"]:
            errors.append(
                "INACTIVE_PRODUCT"
            )

        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        if quantity <= 0:

            errors.append(
                "INVALID_QUANTITY"
            )

        else:

            units_per_case = int(
                master_product["units_per_case"]
            )

            if quantity % units_per_case != 0:
                errors.append(
                    "INVALID_PACKAGE_QUANTITY"
                )

        # ----------------------------------------------------
        # INVENTORY
        # ----------------------------------------------------

        stock_quantity = erp_product[
            "stock_quantity"
        ]

        if quantity > stock_quantity:
            errors.append(
                "INSUFFICIENT_STOCK"
            )

        # ----------------------------------------------------
        # COMMERCIAL VALUES
        # ----------------------------------------------------

        unit_price = erp_product[
            "unit_price"
        ]

        line_total = round(
            quantity * unit_price,
            2,
        )

        return {
            **item,
            "category": master_product["category"],
            "brand": master_product["brand"],
            "units_per_case": int(
                master_product["units_per_case"]
            ),
            "unit_price": unit_price,
            "stock_quantity": stock_quantity,
            "line_total": line_total,
            "errors": errors,
        }