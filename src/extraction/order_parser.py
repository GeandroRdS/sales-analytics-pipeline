import re


class OrderParser:
    """
    Converts extracted purchase order text into structured dictionaries
    and reports lines that could not be interpreted.
    """

    ORDER_PATTERN = re.compile(
        r"PURCHASE ORDER:\s*(PO-\d+)"
        r"\s+Customer:\s*(.+?)"
        r"\s+Customer Code:\s*(.+?)"
        r"\s+Tax ID:\s*(.+?)"
        r"\s+Order Date:\s*(\d{4}-\d{2}-\d{2})"
        r"\s+Product Code Description Quantity"
        r"(.*?)(?=PURCHASE ORDER:|\Z)",
        re.DOTALL,
    )

    ITEM_PATTERN = re.compile(
        r"^(PRD-\d+)\s+(.+?)\s+(-?\d+)$"
    )

    def parse(self, text: str) -> tuple[list[dict], list[dict]]:
        orders = []
        parsing_errors = []

        for match in self.ORDER_PATTERN.finditer(text):

            (
                purchase_order,
                customer_name,
                customer_code,
                tax_id,
                order_date,
                items_text,
            ) = match.groups()

            items, item_errors = self._parse_items(
                purchase_order,
                items_text,
            )

            parsing_errors.extend(item_errors)

            order = {
                "purchase_order": purchase_order.strip(),
                "order_date": order_date.strip(),
                "customer_code": customer_code.strip(),
                "customer_name": customer_name.strip(),
                "tax_id": tax_id.strip(),
                "items": items,
            }

            if not items:
                parsing_errors.append(
                    {
                        "purchase_order": purchase_order,
                        "type": "ORDER_WITHOUT_ITEMS",
                        "content": "",
                    }
                )

            orders.append(order)

        return orders, parsing_errors

    def _parse_items(
        self,
        purchase_order: str,
        items_text: str,
    ) -> tuple[list[dict], list[dict]]:

        items = []
        errors = []

        for line in items_text.splitlines():

            line = line.strip()

            if not line:
                continue

            match = self.ITEM_PATTERN.fullmatch(line)

            if not match:
                errors.append(
                    {
                        "purchase_order": purchase_order,
                        "type": "UNPARSED_ITEM_LINE",
                        "content": line,
                    }
                )
                continue

            product_code, description, quantity = match.groups()

            items.append(
                {
                    "product_code": product_code,
                    "description": description.strip(),
                    "quantity": int(quantity),
                }
            )

        return items, errors