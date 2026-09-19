from pathlib import Path
from datetime import date, timedelta
import json
import random

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUM_CUSTOMERS = 35
NUM_SELLERS = 8
NUM_PRODUCTS = 150
NUM_ORDERS = 300

START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 8, 31)

random.seed(RANDOM_SEED)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw"

PDF_DIR = DATA_DIR / "pdf"
EXCEL_DIR = DATA_DIR / "excel"
SEED_DIR = DATA_DIR / "seed"

PDF_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
SEED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MASTER DATA
# ============================================================

CATEGORIES = [
    "Computers",
    "Monitors",
    "Peripherals",
    "Networking",
    "Storage",
    "Accessories",
    "Audio",
    "Office Equipment",
]

BRANDS = [
    "Nexora",
    "Visionix",
    "ByteCore",
    "Orbitek",
    "Veltrix",
    "Axion",
]

PRODUCT_TYPES = {
    "Computers": [
        "Business Laptop",
        "Professional Laptop",
        "Mini Desktop",
        "Office Desktop",
        "Workstation",
    ],
    "Monitors": [
        '22" Full HD Monitor',
        '24" Full HD Monitor',
        '27" QHD Monitor',
        '32" UHD Monitor',
    ],
    "Peripherals": [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "Wireless Keyboard",
        "Webcam",
        "USB Keyboard",
    ],
    "Networking": [
        "Gigabit Router",
        "Wi-Fi 6 Router",
        "8-Port Switch",
        "16-Port Switch",
        "24-Port Switch",
    ],
    "Storage": [
        "256GB SSD",
        "512GB SSD",
        "1TB SSD",
        "2TB External Drive",
        "4TB External Drive",
    ],
    "Accessories": [
        "USB-C Hub",
        "Notebook Stand",
        "HDMI Cable",
        "USB-C Cable",
        "Laptop Backpack",
    ],
    "Audio": [
        "USB Headset",
        "Wireless Headset",
        "Desktop Speakers",
        "Conference Speaker",
    ],
    "Office Equipment": [
        "Document Scanner",
        "Label Printer",
        "Barcode Scanner",
        "Thermal Printer",
    ],
}

CUSTOMER_PREFIXES = [
    "Alpha",
    "Prime",
    "Nova",
    "Vertex",
    "Blue",
    "Smart",
    "Digital",
    "Central",
    "Next",
    "Global",
    "Quantum",
    "Dynamic",
    "Advance",
    "United",
    "Vision",
    "Core",
    "Rapid",
    "Superior",
    "Metro",
    "Summit",
    "Pioneer",
    "Integra",
    "Atlas",
    "Omega",
    "Fusion",
    "Bright",
    "Apex",
    "Everest",
    "Sterling",
    "Horizon",
    "Matrix",
    "Titan",
    "Orbit",
    "Velocity",
    "Infinity",
]

CUSTOMER_SUFFIXES = [
    "Technology",
    "Solutions",
    "Systems",
    "Retail",
    "Business",
    "Commerce",
    "Enterprises",
    "Supplies",
]

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

SELLER_NAMES = [
    "Olivia Carter",
    "Ethan Brooks",
    "Sophia Turner",
    "Liam Parker",
    "Emma Collins",
    "Noah Bennett",
    "Ava Mitchell",
    "Lucas Morgan",
]


# ============================================================
# HELPERS
# ============================================================

def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def write_json(path: Path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def generate_fake_tax_id(index: int) -> str:
    """
    Generates an intentionally synthetic identifier.

    It resembles a business identifier for demonstration purposes,
    but it is not intended to represent a valid real-world tax ID.
    """
    return f"99.{index:03d}.{(index * 17) % 1000:03d}/0001-{(index * 7) % 100:02d}"


# ============================================================
# SELLERS
# ============================================================

def generate_sellers():
    sellers = []

    for index, name in enumerate(SELLER_NAMES, start=1):
        sellers.append(
            {
                "seller_id": index,
                "seller_code": f"SEL-{index:03d}",
                "seller_name": name,
                "region": REGIONS[(index - 1) % len(REGIONS)],
                "active": True,
            }
        )

    return sellers


# ============================================================
# CUSTOMERS
# ============================================================

def generate_customers(sellers):
    customers = []

    for index in range(1, NUM_CUSTOMERS + 1):

        prefix = CUSTOMER_PREFIXES[index - 1]
        suffix = random.choice(CUSTOMER_SUFFIXES)

        seller = random.choice(sellers)

        customer = {
            "customer_id": index,
            "customer_code": f"CUS-{index:04d}",
            "customer_name": f"{prefix} {suffix}",
            "tax_id": generate_fake_tax_id(index),
            "region": seller["region"],
            "seller_id": seller["seller_id"],
            "credit_limit": random.choice(
                [25000, 50000, 75000, 100000, 150000, 200000]
            ),
            "active": True,
        }

        customers.append(customer)

    # Intentionally create a few inactive customers
    inactive_customers = random.sample(customers, 2)

    for customer in inactive_customers:
        customer["active"] = False

    return customers


# ============================================================
# PRODUCTS
# ============================================================

def generate_products():
    products = []

    for index in range(1, NUM_PRODUCTS + 1):

        category = CATEGORIES[(index - 1) % len(CATEGORIES)]
        brand = random.choice(BRANDS)
        product_type = random.choice(PRODUCT_TYPES[category])

        units_per_case = random.choice([1, 2, 5, 10, 20])

        unit_price = round(
            random.uniform(15, 2500),
            2,
        )

        product = {
            "product_id": index,
            "product_code": f"PRD-{index:04d}",
            "description": f"{brand} {product_type}",
            "category": category,
            "brand": brand,
            "units_per_case": units_per_case,
            "unit_price": unit_price,
            "active": True,
        }

        products.append(product)

    # A few intentionally inactive products
    inactive_products = random.sample(products, 4)

    for product in inactive_products:
        product["active"] = False

    return products


# ============================================================
# INVENTORY
# ============================================================

def generate_inventory(products):
    inventory = []

    for product in products:
        inventory.append(
            {
                "product_id": product["product_id"],
                "product_code": product["product_code"],
                "stock_quantity": random.randint(50, 2000),
            }
        )

    return inventory


# ============================================================
# ORDERS
# ============================================================

def generate_orders(customers, products):
    orders = []

    for order_index in range(1, NUM_ORDERS + 1):

        customer = random.choice(customers)

        order = {
            "purchase_order": f"PO-{order_index:06d}",
            "order_date": random_date(
                START_DATE,
                END_DATE,
            ).isoformat(),
            "customer_code": customer["customer_code"],
            "customer_name": customer["customer_name"],
            "tax_id": customer["tax_id"],
            "items": [],
        }

        number_of_items = random.randint(2, 10)

        selected_products = random.sample(
            products,
            number_of_items,
        )

        for product in selected_products:

            number_of_cases = random.randint(1, 15)

            quantity = (
                number_of_cases
                * product["units_per_case"]
            )

            order["items"].append(
                {
                    "product_code": product["product_code"],
                    "description": product["description"],
                    "quantity": quantity,
                }
            )

        orders.append(order)

    add_order_anomalies(orders)

    return orders


# ============================================================
# DATA QUALITY ANOMALIES
# ============================================================

def add_order_anomalies(orders):
    """
    Adds controlled problems to the synthetic orders.

    These anomalies will later be detected by the validation pipeline.
    """

    # Unknown products
    for order in random.sample(orders, 5):
        order["items"][0]["product_code"] = "PRD-9999"
        order["items"][0]["description"] = "Unknown Product"

    # Invalid quantities
    for order in random.sample(orders, 5):
        order["items"][0]["quantity"] = 0

    # Quantities that may violate package configuration
    for order in random.sample(orders, 8):
        order["items"][0]["quantity"] += 1

    # Unknown customers
    for order in random.sample(orders, 3):
        order["tax_id"] = "00.000.000/0000-00"
        order["customer_code"] = "UNKNOWN"

    # Duplicate purchase orders
    duplicate_sources = random.sample(orders, 3)

    for source in duplicate_sources:
        duplicate = {
            "purchase_order": source["purchase_order"],
            "order_date": source["order_date"],
            "customer_code": source["customer_code"],
            "customer_name": source["customer_name"],
            "tax_id": source["tax_id"],
            "items": [
                item.copy()
                for item in source["items"]
            ],
        }

        orders.append(duplicate)


# ============================================================
# EXCEL PRODUCT MASTER
# ============================================================

def generate_product_master_excel(products):
    dataframe = pd.DataFrame(
        [
            {
                "product_code": product["product_code"],
                "description": product["description"],
                "category": product["category"],
                "brand": product["brand"],
                "units_per_case": product["units_per_case"],
            }
            for product in products
        ]
    )

    output_path = (
        EXCEL_DIR
        / "product_master.xlsx"
    )

    dataframe.to_excel(
        output_path,
        index=False,
        sheet_name="Products",
    )

    return output_path


# ============================================================
# PDF
# ============================================================

def generate_orders_pdf(orders):
    output_path = (
        PDF_DIR
        / "purchase_orders_batch.pdf"
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "CONSOLIDATED PURCHASE ORDERS",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "Synthetic document generated for portfolio demonstration.",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 10 * mm))

    for index, order in enumerate(orders):

        story.append(
            Paragraph(
                f"PURCHASE ORDER: {order['purchase_order']}",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                f"Customer: {order['customer_name']}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"Customer Code: {order['customer_code']}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"Tax ID: {order['tax_id']}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"Order Date: {order['order_date']}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 5 * mm))

        table_data = [
            [
                "Product Code",
                "Description",
                "Quantity",
            ]
        ]

        for item in order["items"]:
            table_data.append(
                [
                    item["product_code"],
                    item["description"],
                    str(item["quantity"]),
                ]
            )

        table = Table(
            table_data,
            colWidths=[
                35 * mm,
                105 * mm,
                25 * mm,
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "ALIGN",
                        (2, 1),
                        (2, -1),
                        "RIGHT",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        story.append(table)

        if index < len(orders) - 1:
            story.append(PageBreak())

    document.build(story)

    return output_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("GENERATING SYNTHETIC BUSINESS DATA")
    print("=" * 60)

    sellers = generate_sellers()
    customers = generate_customers(sellers)
    products = generate_products()
    inventory = generate_inventory(products)
    orders = generate_orders(customers, products)

    write_json(
        SEED_DIR / "sellers.json",
        sellers,
    )

    write_json(
        SEED_DIR / "customers.json",
        customers,
    )

    write_json(
        SEED_DIR / "products.json",
        products,
    )

    write_json(
        SEED_DIR / "inventory.json",
        inventory,
    )

    excel_path = generate_product_master_excel(
        products
    )

    pdf_path = generate_orders_pdf(
        orders
    )

    total_items = sum(
        len(order["items"])
        for order in orders
    )

    print()
    print("Generation completed successfully.")
    print()
    print(f"Sellers:       {len(sellers)}")
    print(f"Customers:     {len(customers)}")
    print(f"Products:      {len(products)}")
    print(f"Orders:        {len(orders)}")
    print(f"Order items:   {total_items}")
    print()
    print(f"Excel: {excel_path}")
    print(f"PDF:   {pdf_path}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()