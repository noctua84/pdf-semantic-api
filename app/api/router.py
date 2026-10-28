from fastapi import APIRouter

from app.api import ingest_pdf, search_pdf

router = APIRouter()

router.include_router(ingest_pdf.router, tags=["ingest"])
router.include_router(search_pdf.router, tags=["search"])