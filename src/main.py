from collections import Counter
from pathlib import Path

from data.product_master import ProductMaster
from extraction.order_parser import OrderParser
from extraction.pdf_extractor import PDFExtractor
from integration.erp_client import ERPClient
from validation.order_validator import OrderValidator
from output.excel_report import ExcelReportGenerator


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "pdf"
    / "purchase_orders_batch.pdf"
)

PRODUCT_MASTER_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "excel"
    / "product_master.xlsx"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "output"
    / "processed_orders.xlsx"
)


def main():

    print("=" * 60)
    print("SALES ORDER AUTOMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # EXTRACTION
    # --------------------------------------------------------

    print()
    print("Reading purchase orders PDF...")

    extractor = PDFExtractor()

    text = extractor.extract_text(
        PDF_PATH
    )

    # --------------------------------------------------------
    # PARSING
    # --------------------------------------------------------

    print("Parsing purchase orders...")

    parser = OrderParser()

    orders, parsing_errors = parser.parse(
        text
    )

    total_items = sum(
        len(order["items"])
        for order in orders
    )

    print(
        f"Parsed {len(orders):,} order records "
        f"and {total_items:,} items."
    )

    if parsing_errors:
        print(
            f"Warning: {len(parsing_errors):,} "
            f"parsing errors detected."
        )

    # --------------------------------------------------------
    # PRODUCT MASTER
    # --------------------------------------------------------

    print()
    print("Loading product master...")

    product_master = ProductMaster(
        PRODUCT_MASTER_PATH
    )

    print(
        f"Loaded "
        f"{len(product_master.products):,} products."
    )

    # --------------------------------------------------------
    # ERP API
    # --------------------------------------------------------

    print("Connecting to ERP API...")

    erp = ERPClient()

    # Simple connection test
    erp.get_customer(
        "CUS-0014"
    )

    print(
        "ERP API connection successful."
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print("Validating orders...")

    validator = OrderValidator(
        erp_client=erp,
        product_master=product_master,
    )

    results = validator.validate_orders(
        orders
    )

    # --------------------------------------------------------
    # APPROVED / REJECTED
    # --------------------------------------------------------

    approved = [
        result
        for result in results
        if result["status"] == "APPROVED"
    ]

    rejected = [
        result
        for result in results
        if result["status"] == "REJECTED"
    ]

    # --------------------------------------------------------
    # ERROR COUNTERS
    # --------------------------------------------------------

    order_error_counter = Counter()
    item_error_counter = Counter()

    for result in rejected:

        # Errors affecting the order
        order_error_counter.update(
            result["errors"]
        )

        # Errors affecting individual items
        for item in result["items"]:

            item_error_counter.update(
                item["errors"]
            )

    # --------------------------------------------------------
    # PROCESSING SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    print(
        f"Order records:     "
        f"{len(results):,}"
    )

    print(
        f"Approved orders:   "
        f"{len(approved):,}"
    )

    print(
        f"Rejected orders:   "
        f"{len(rejected):,}"
    )

    approval_rate = (
        len(approved)
        / len(results)
        * 100
        if results
        else 0
    )

    print(
        f"Approval rate:     "
        f"{approval_rate:.2f}%"
    )

    print(
        f"Parsing errors:    "
        f"{len(parsing_errors):,}"
    )

    # --------------------------------------------------------
    # ORDER-LEVEL REJECTION REASONS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("REJECTION REASONS")
    print("=" * 60)

    if order_error_counter:

        print("Order-level impact:")
        print()

        for error, quantity in (
            order_error_counter.most_common()
        ):

            print(
                f"{error:<30} "
                f"{quantity:>5}"
            )

    else:

        print(
            "No rejected orders."
        )

    # --------------------------------------------------------
    # ITEM-LEVEL VALIDATION ERRORS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ITEM VALIDATION ERRORS")
    print("=" * 60)

    if item_error_counter:

        for error, quantity in (
            item_error_counter.most_common()
        ):

            print(
                f"{error:<30} "
                f"{quantity:>5}"
            )

    else:

        print(
            "No item validation errors."
        )

    # --------------------------------------------------------
    # SAMPLE REJECTED ORDER
    # --------------------------------------------------------

    if rejected:

        sample = rejected[0]

        print()
        print("=" * 60)
        print("SAMPLE REJECTED ORDER")
        print("=" * 60)

        print(
            f"Purchase Order: "
            f"{sample['purchase_order']}"
        )

        print(
            f"Customer: "
            f"{sample['customer_name']}"
        )

        print(
            "Reasons: "
            + ", ".join(
                sample["errors"]
            )
        )

        print()

        for item in sample["items"]:

            if item["errors"]:

                print(
                    f"{item['product_code']} | "
                    f"Qty: {item['quantity']} | "
                    + ", ".join(
                        item["errors"]
                    )
                )

        # --------------------------------------------------------
    # EXCEL OUTPUT
    # --------------------------------------------------------

    print()
    print("Generating operational Excel report...")

    report_generator = ExcelReportGenerator()

    report_generator.generate(
        results=results,
        parsing_errors=parsing_errors,
        output_path=OUTPUT_PATH,
    )

    print(
        f"Excel report generated: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()