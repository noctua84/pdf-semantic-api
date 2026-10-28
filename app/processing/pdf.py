import io

from pypdf import PdfReader

from app.processing.dto import ExtractedDocument, ExtractedPage


def extract_pdf_pages(pdf_bytes: bytes) -> ExtractedDocument:
    """Extract text from each page of a PDF file.

    Note: page_count is the PDF's own page count, while pages holds only the
    pages text could be extracted from, so a scanned or image-only page is
    counted but carries no text.
    """

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[ExtractedPage] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())

        if text.strip():
            pages.append(ExtractedPage(page_number, text))

    return ExtractedDocument(page_count=len(reader.pages), pages=pages)
