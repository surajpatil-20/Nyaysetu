"""
NYAYASETU Document Processing — Text Chunking Service

Splits extracted document text into overlapping chunks suitable
for semantic search and RAG retrieval.

Strategy:
  - Target 500-800 tokens per chunk (approximated as ~600 words)
  - 50-100 token overlap between consecutive chunks
  - Respect paragraph boundaries (double-newline)
  - Preserve page-number metadata via [Page N] markers inserted by extraction.py
  - Idempotent: deletes existing chunks for a document before re-chunking
"""
import logging
import re
from typing import Optional

from django.db import transaction

logger = logging.getLogger(__name__)

# Approximate token counts: 1 token ≈ 0.75 words (English)
TARGET_TOKENS = 600          # ~450 words
OVERLAP_TOKENS = 75          # ~56 words
WORDS_PER_TOKEN = 0.75

TARGET_WORDS = int(TARGET_TOKENS * WORDS_PER_TOKEN)      # ~450
OVERLAP_WORDS = int(OVERLAP_TOKENS * WORDS_PER_TOKEN)    # ~56


def _approx_tokens(text: str) -> int:
    """Rough token count: words / 0.75."""
    words = len(text.split())
    return max(1, round(words / WORDS_PER_TOKEN))


def _split_into_paragraphs(text: str) -> list[tuple[Optional[int], str]]:
    """
    Split text into (page_number, paragraph) tuples.
    Respects [Page N] markers inserted during extraction.
    """
    paragraphs = []
    current_page = None
    current_para = []

    for line in text.split('\n'):
        page_match = re.match(r'^\[Page (\d+)\]$', line.strip())
        if page_match:
            # Flush current paragraph
            if current_para:
                para_text = ' '.join(current_para).strip()
                if para_text:
                    paragraphs.append((current_page, para_text))
                current_para = []
            current_page = int(page_match.group(1))
            continue

        if line.strip() == "":
            # Blank line = paragraph boundary
            if current_para:
                para_text = ' '.join(current_para).strip()
                if para_text:
                    paragraphs.append((current_page, para_text))
                current_para = []
        else:
            current_para.append(line.strip())

    # Flush final paragraph
    if current_para:
        para_text = ' '.join(current_para).strip()
        if para_text:
            paragraphs.append((current_page, para_text))

    return paragraphs


def _build_chunks(paragraphs: list[tuple[Optional[int], str]]) -> list[dict]:
    """
    Group paragraphs into chunks with overlap.

    Returns list of:
        {
          "content": str,
          "page_number": int or None,
          "token_count": int,
          "chunk_index": int (0-based),
        }
    """
    chunks = []
    buffer_words: list[str] = []
    buffer_pages: list[Optional[int]] = []
    chunk_index = 0

    def flush_chunk(words, pages):
        nonlocal chunk_index
        if not words:
            return
        content = ' '.join(words)
        # Use the first page seen in this chunk
        page = next((p for p in pages if p is not None), None)
        chunks.append({
            "content": content,
            "page_number": page,
            "token_count": _approx_tokens(content),
            "chunk_index": chunk_index,
        })
        chunk_index += 1

    for page_num, para in paragraphs:
        para_words = para.split()
        para_pages = [page_num] * len(para_words)

        buffer_words.extend(para_words)
        buffer_pages.extend(para_pages)

        # Flush when target size exceeded
        while len(buffer_words) >= TARGET_WORDS:
            flush_chunk(buffer_words[:TARGET_WORDS], buffer_pages[:TARGET_WORDS])
            # Keep overlap
            keep = OVERLAP_WORDS
            buffer_words = buffer_words[TARGET_WORDS - keep:]
            buffer_pages = buffer_pages[TARGET_WORDS - keep:]

    # Final flush
    flush_chunk(buffer_words, buffer_pages)

    return chunks


@transaction.atomic
def chunk_document(document, force_rechunk: bool = False) -> int:
    """
    Chunk a Document model instance and store DocumentChunk records.

    Returns the number of chunks created.
    """
    from apps.documents.models import DocumentChunk

    if not document.extracted_text:
        logger.warning("Document #%d has no extracted_text; skipping chunking.", document.pk)
        return 0

    # Idempotency: delete existing chunks before re-chunking
    existing_count = DocumentChunk.objects.filter(document=document).count()
    if existing_count > 0 and not force_rechunk:
        logger.info("Document #%d already has %d chunks; use force_rechunk=True to rechunk.", document.pk, existing_count)
        return existing_count

    DocumentChunk.objects.filter(document=document).delete()
    logger.info("Chunking Document #%d...", document.pk)

    paragraphs = _split_into_paragraphs(document.extracted_text)
    raw_chunks = _build_chunks(paragraphs)

    if not raw_chunks:
        # Fallback: treat entire text as one chunk
        raw_chunks = [{
            "content": document.extracted_text[:4000],
            "page_number": 1,
            "token_count": _approx_tokens(document.extracted_text),
            "chunk_index": 0,
        }]

    created = 0
    for chunk_data in raw_chunks:
        DocumentChunk.objects.create(
            document=document,
            case=document.case,
            chunk_index=chunk_data["chunk_index"],
            content=chunk_data["content"],
            page_number=chunk_data["page_number"],
            token_count=chunk_data["token_count"],
        )
        created += 1

    logger.info("Document #%d: created %d chunks.", document.pk, created)
    return created

