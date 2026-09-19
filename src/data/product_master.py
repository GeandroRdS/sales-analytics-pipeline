from pathlib import Path

import pandas as pd


class ProductMaster:
    """
    Loads complementary product information from Excel.
    """

    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self.products = {}

        self._load()

    def _load(self):

        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"Product master not found: {self.excel_path}"
            )

        dataframe = pd.read_excel(
            self.excel_path,
            sheet_name="Products",
        )

        required_columns = {
            "product_code",
            "description",
            "category",
            "brand",
            "units_per_case",
        }

        missing_columns = (
            required_columns
            - set(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Missing columns in product master: "
                + ", ".join(sorted(missing_columns))
            )

        for record in dataframe.to_dict(
            orient="records"
        ):
            self.products[
                record["product_code"]
            ] = record

    def get_product(
        self,
        product_code: str,
    ) -> dict | None:

        return self.products.get(product_code)