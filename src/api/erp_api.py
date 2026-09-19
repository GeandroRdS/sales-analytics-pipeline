from pathlib import Path
import json

from fastapi import FastAPI, HTTPException


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SEED_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "seed"
)


def load_json(filename: str) -> list[dict]:
    path = SEED_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Seed file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


customers = load_json("customers.json")
products = load_json("products.json")
inventory = load_json("inventory.json")
sellers = load_json("sellers.json")


customer_by_code = {
    customer["customer_code"]: customer
    for customer in customers
}

product_by_code = {
    product["product_code"]: product
    for product in products
}

inventory_by_product = {
    item["product_code"]: item
    for item in inventory
}

seller_by_id = {
    seller["seller_id"]: seller
    for seller in sellers
}


app = FastAPI(
    title="Synthetic ERP API",
    description=(
        "REST API simulating ERP master data "
        "for the Sales Order Automation project."
    ),
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "service": "Synthetic ERP API",
        "status": "running",
    }


@app.get("/api/customers/{customer_code}")
def get_customer(customer_code: str):

    customer = customer_by_code.get(
        customer_code
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    result = customer.copy()

    seller = seller_by_id.get(
        customer["seller_id"]
    )

    if seller:
        result["seller"] = {
            "seller_id": seller["seller_id"],
            "seller_code": seller["seller_code"],
            "seller_name": seller["seller_name"],
            "region": seller["region"],
        }

    return result


@app.get("/api/products/{product_code}")
def get_product(product_code: str):

    product = product_by_code.get(
        product_code
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    result = product.copy()

    stock = inventory_by_product.get(
        product_code
    )

    result["stock_quantity"] = (
        stock["stock_quantity"]
        if stock
        else 0
    )

    return result


@app.get("/api/inventory/{product_code}")
def get_inventory(product_code: str):

    stock = inventory_by_product.get(
        product_code
    )

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found",
        )

    return stock


@app.get("/api/sellers/{seller_id}")
def get_seller(seller_id: int):

    seller = seller_by_id.get(
        seller_id
    )

    if seller is None:
        raise HTTPException(
            status_code=404,
            detail="Seller not found",
        )

    return seller