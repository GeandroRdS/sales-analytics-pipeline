from pathlib import Path

import pdfplumber


class PDFExtractor:
    """
    Extracts raw text from PDF documents.

    This class is responsible only for reading the PDF.
    It does not contain business rules or order parsing logic.
    """

    def extract_text(self, pdf_path: Path) -> str:

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        pages_text = []

        with pdfplumber.open(pdf_path) as pdf:

            for page_number, page in enumerate(
                pdf.pages,
                start=1,
            ):

                text = page.extract_text()

                if text:
                    pages_text.append(text)

                else:
                    print(
                        f"Warning: no text found "
                        f"on page {page_number}"
                    )

        return "\n".join(pages_text)