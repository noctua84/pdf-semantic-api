from app.processing.dto import ExtractedPage, ExtractedChunk


def chunk_pages(pages: list[ExtractedPage], chunk_size: int, chunk_overlap: int) -> list[ExtractedChunk]:
    """
    Breaks a list of pages into chunks of text.

    Note: In a production system I would consider section-aware chunking,
    heading detection, table handling, and OCR for scanned PDFs.

    :param pages:
    :param chunk_size:
    :param chunk_overlap:
    :return:
    """
    chunks: list[ExtractedChunk] = []
    global_chunk_index = 0
    step = max(1, chunk_size - chunk_overlap)

    for page in pages:
        start = 0

        while start < len(page.text):
            end = min(start + chunk_size, len(page.text))
            text = page.text[start:end].strip()

            if text:
                chunk = ExtractedChunk(
                    text=text,
                    page_number=page.page_number,
                    chunk_index=global_chunk_index,
                )
                chunks.append(chunk)
                global_chunk_index += 1

            if end >= len(page.text):
                break

            start += step

    return chunks
