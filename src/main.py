from pathlib import Path

from extraction.pdf_extractor import PDFExtractor
from extraction.order_parser import OrderParser


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "pdf"
    / "purchase_orders_batch.pdf"
)


def main():

    print("=" * 60)
    print("SALES ORDER AUTOMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # PDF EXTRACTION
    # --------------------------------------------------------

    print()
    print("Reading purchase orders PDF...")

    extractor = PDFExtractor()
    text = extractor.extract_text(PDF_PATH)

    print("PDF successfully processed.")

    # --------------------------------------------------------
    # ORDER PARSING
    # --------------------------------------------------------

    print()
    print("Parsing purchase orders...")

    parser = OrderParser()

    orders, parsing_errors = parser.parse(text)

    total_items = sum(
        len(order["items"])
        for order in orders
    )

    unique_purchase_orders = {
        order["purchase_order"]
        for order in orders
    }

    duplicate_records = (
        len(orders)
        - len(unique_purchase_orders)
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PARSING SUMMARY")
    print("=" * 60)

    print(f"Characters extracted:      {len(text):,}")
    print(f"Order records extracted:   {len(orders):,}")
    print(f"Unique purchase orders:    {len(unique_purchase_orders):,}")
    print(f"Duplicate order records:   {duplicate_records:,}")
    print(f"Items extracted:           {total_items:,}")
    print(f"Parsing errors:            {len(parsing_errors):,}")

    # --------------------------------------------------------
    # PARSING ERRORS
    # --------------------------------------------------------

    if parsing_errors:

        print()
        print("=" * 60)
        print("PARSING ERRORS")
        print("=" * 60)

        for error in parsing_errors[:10]:
            print(
                f"{error['purchase_order']} | "
                f"{error['type']} | "
                f"{error['content']}"
            )

        if len(parsing_errors) > 10:
            print(
                f"... and {len(parsing_errors) - 10} more errors."
            )

    # --------------------------------------------------------
    # SAMPLE ORDER
    # --------------------------------------------------------

    if orders:

        first_order = orders[0]

        print()
        print("=" * 60)
        print("FIRST ORDER")
        print("=" * 60)

        print(
            f"Purchase Order: {first_order['purchase_order']}"
        )

        print(
            f"Customer:       {first_order['customer_name']}"
        )

        print(
            f"Customer Code:  {first_order['customer_code']}"
        )

        print(
            f"Tax ID:         {first_order['tax_id']}"
        )

        print(
            f"Order Date:     {first_order['order_date']}"
        )

        print()
        print("Items:")

        for item in first_order["items"]:

            print(
                f"  {item['product_code']} | "
                f"{item['description']} | "
                f"Qty: {item['quantity']}"
            )


if __name__ == "__main__":
    main()