"""
NYAYASETU Document Processing — PDF Text Extraction Service

Uses PyMuPDF (fitz) to extract text from judicial PDFs.
Falls back gracefully if the library is unavailable.

Workflow:
  1. Open PDF with fitz.open()
  2. Extract text page-by-page
  3. If total text is sparse (< 50 chars per page avg) → flag as OCR_REQUIRED
  4. Clean extracted text (normalize whitespace, remove boilerplate artifacts)
  5. Update Document.extracted_text, .extraction_status, .page_count
"""
import logging
import os
import re
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF (fitz) not available; PDF extraction will be skipped.")

# Minimum average characters per page to consider direct text extraction sufficient
MIN_CHARS_PER_PAGE = 50

# Path to Tesseract traineddata directory for PyMuPDF built-in OCR
TESSDATA_DIR = os.path.join(settings.BASE_DIR, 'data', 'tessdata')


def _clean_text(text: str) -> str:
    """
    Basic text cleanup for judicial document text.
    - Normalize unicode whitespace
    - Collapse multiple blank lines
    - Strip trailing spaces per line
    """
    text = text.replace('\xa0', ' ').replace('\x0c', '\n')
    lines = text.split('\n')
    lines = [re.sub(r'[ \t]+', ' ', line).rstrip() for line in lines]
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def extract_ocr_from_page(page, tessdata_dir: Optional[str] = None) -> str:
    """
    Perform local OCR on an individual PDF page using PyMuPDF's built-in
    Tesseract C-API integration.
    """
    tdir = tessdata_dir or TESSDATA_DIR
    try:
        tp = page.get_textpage_ocr(language="eng", tessdata=tdir, dpi=150)
        return page.get_text("text", textpage=tp)
    except Exception as exc:
        logger.warning("OCR extraction failed for page %d: %s", page.number, exc)
        return ""


def extract_text_from_file(filepath: str) -> dict:
    """
    Extract text from a PDF file using:
      1. Direct PyMuPDF text stream extraction
      2. If extracted text is insufficient (< 50 chars/page), automatic OCR fallback

    Returns:
        {
          "success": bool,
          "pages": {page_num: text, ...},   # 1-indexed
          "full_text": str,
          "page_count": int,
          "used_ocr": bool,
          "error": str or None,
        }
    """
    result = {
        "success": False,
        "pages": {},
        "full_text": "",
        "page_count": 0,
        "used_ocr": False,
        "error": None,
    }

    if not PYMUPDF_AVAILABLE:
        result["error"] = "PyMuPDF not installed"
        return result

    try:
        doc = fitz.open(filepath)
        result["page_count"] = len(doc)
        pages = {}
        total_chars = 0

        # Step 1: Attempt standard text extraction
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            cleaned = _clean_text(text)
            pages[page_num + 1] = cleaned
            total_chars += len(cleaned)

        avg_chars = total_chars / max(result["page_count"], 1)

        # Step 2: If text is sparse, execute OCR fallback on pages
        if avg_chars < MIN_CHARS_PER_PAGE:
            logger.info("PDF '%s' has sparse text (avg %.0f chars/page). Running PyMuPDF OCR fallback...", filepath, avg_chars)
            ocr_pages = {}
            ocr_total_chars = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                # If page had very little text, apply OCR
                if len(pages.get(page_num + 1, "")) < MIN_CHARS_PER_PAGE:
                    ocr_raw = extract_ocr_from_page(page)
                    cleaned_ocr = _clean_text(ocr_raw)
                    if len(cleaned_ocr) > len(pages.get(page_num + 1, "")):
                        ocr_pages[page_num + 1] = cleaned_ocr
                        ocr_total_chars += len(cleaned_ocr)
                    else:
                        ocr_pages[page_num + 1] = pages.get(page_num + 1, "")
                        ocr_total_chars += len(pages.get(page_num + 1, ""))
                else:
                    ocr_pages[page_num + 1] = pages.get(page_num + 1, "")
                    ocr_total_chars += len(pages.get(page_num + 1, ""))

            if ocr_total_chars > total_chars:
                pages = ocr_pages
                result["used_ocr"] = True
                logger.info("OCR successfully recovered %d characters across document.", ocr_total_chars)

        doc.close()

        result["pages"] = pages
        result["full_text"] = '\n\n'.join(
            f"[Page {p}]\n{t}" for p, t in sorted(pages.items()) if t
        )

        if result["full_text"].strip():
            result["success"] = True
        elif result["page_count"] > 0:
            result["success"] = False
            result["error"] = "Document contains pages but yielded no readable text even after OCR."

    except Exception as exc:
        result["error"] = str(exc)
        logger.exception("Failed to extract text from '%s': %s", filepath, exc)

    return result


def process_document(document) -> bool:
    """
    Process a Document model instance:
    - Extract text from its file (with OCR fallback when needed)
    - Update extraction_status, extracted_text, page_count

    Returns True on success, False on failure.
    """
    from apps.documents.models import Document

    if not document.file:
        logger.warning("Document #%d has no file attached; skipping.", document.pk)
        document.extraction_status = Document.ExtractionStatus.FAILED
        document.save(update_fields=["extraction_status"])
        return False

    filepath = document.file.path
    logger.info("Processing Document #%d: %s", document.pk, filepath)

    extraction = extract_text_from_file(filepath)

    if not extraction["success"]:
        document.extraction_status = Document.ExtractionStatus.FAILED
        document.page_count = extraction.get("page_count")
        document.save(update_fields=["extraction_status", "page_count"])
        logger.error("Document #%d extraction failed: %s", document.pk, extraction.get("error"))
        return False

    document.extracted_text = extraction["full_text"]
    document.page_count = extraction["page_count"]
    document.extraction_status = Document.ExtractionStatus.COMPLETED
    document.save(update_fields=["extracted_text", "page_count", "extraction_status"])
    logger.info("Document #%d processed successfully (%d pages, used_ocr=%s).",
                document.pk, extraction["page_count"], extraction["used_ocr"])
    return True

