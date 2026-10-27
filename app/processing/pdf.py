import io

from pypdf import PdfReader

from app.processing.dto import ExtractedPage


def extract_pdf_pages(pdf_bytes: bytes) -> list[ExtractedPage]:
    """Extract text from each page of a PDF file."""

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[ExtractedPage] = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = " ".join(text.split())

        if text.strip():
            pages.append(ExtractedPage(page_number, text))

    return pages
