import requests


class ERPClient:
    """
    HTTP client responsible for communication with the ERP REST API.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_customer(
        self,
        customer_code: str,
    ) -> dict | None:

        return self._get(
            f"/api/customers/{customer_code}"
        )

    def get_product(
        self,
        product_code: str,
    ) -> dict | None:

        return self._get(
            f"/api/products/{product_code}"
        )

    def get_inventory(
        self,
        product_code: str,
    ) -> dict | None:

        return self._get(
            f"/api/inventory/{product_code}"
        )

    def get_seller(
        self,
        seller_id: int,
    ) -> dict | None:

        return self._get(
            f"/api/sellers/{seller_id}"
        )

    def _get(
        self,
        endpoint: str,
    ) -> dict | None:

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
            )

        except requests.RequestException as exc:
            raise ConnectionError(
                f"Could not communicate with ERP API: {url}"
            ) from exc

        if response.status_code == 404:
            return None

        try:
            response.raise_for_status()

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"ERP API returned "
                f"HTTP {response.status_code}: {url}"
            ) from exc

        return response.json()