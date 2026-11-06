"""
NYAYASETU Document Processing — Embedding Service

Generates dense 768-dim sentence embeddings using sentence-transformers.
Stores embeddings directly in PostgreSQL pgvector DocumentChunk.embedding (VectorField).

Design decisions:
  - Uses BAAI/bge-base-en-v1.5 by default (768 dims, optimized for legal text retrieval)
  - Falls back to a mock zero-vector if sentence-transformers is unavailable
  - Skips chunks that already have embeddings (unless force=True)
  - Processes and updates in configurable batches
"""
import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = getattr(settings, "EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5")
EMBEDDING_DIMENSION = getattr(settings, "EMBEDDING_DIMENSION", 768)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning(
        "sentence-transformers not installed. "
        "Run: pip install sentence-transformers  to enable real embeddings. "
        "Falling back to zero-vector mock embeddings."
    )

_model_cache: Optional[object] = None


def _get_model():
    """Lazy-load the embedding model (singleton per process)."""
    global _model_cache
    if _model_cache is None:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return None
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _model_cache = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _model_cache


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts. Returns list of float lists (each 768 dims).
    If sentence-transformers unavailable, returns zero vectors.
    """
    if not texts:
        return []

    model = _get_model()
    if model is None:
        logger.warning("Using mock zero-vector embeddings (sentence-transformers not installed).")
        return [[0.0] * EMBEDDING_DIMENSION for _ in texts]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return [emb.tolist() for emb in embeddings]


def embed_single(text: str) -> list[float]:
    """Embed a single text string."""
    result = embed_texts([text])
    return result[0] if result else [0.0] * EMBEDDING_DIMENSION


def generate_embeddings_for_document(document, force: bool = False, batch_size: int = 32) -> dict:
    """
    Generate embeddings for all DocumentChunks of a document.

    Args:
        document: Document model instance
        force: Re-embed even if embedding already exists
        batch_size: Number of chunks to embed in a single model call

    Returns:
        {"processed": int, "skipped": int, "errors": int}
    """
    from apps.documents.models import DocumentChunk

    chunks = DocumentChunk.objects.filter(document=document).order_by("chunk_index")
    summary = {"processed": 0, "skipped": 0, "errors": 0}

    if not force:
        chunks = chunks.filter(embedding__isnull=True)

    chunks_list = list(chunks)
    if not chunks_list:
        logger.info("Document #%d: no chunks need embedding.", document.pk)
        return summary

    logger.info("Generating embeddings for Document #%d (%d chunks)...", document.pk, len(chunks_list))

    # Process in batches
    for i in range(0, len(chunks_list), batch_size):
        batch = chunks_list[i:i + batch_size]
        texts = [chunk.content for chunk in batch]
        try:
            vectors = embed_texts(texts)
            for chunk, vector in zip(batch, vectors):
                if len(vector) != EMBEDDING_DIMENSION:
                    raise ValueError(f"Embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {len(vector)}")
                chunk.embedding = vector
            DocumentChunk.objects.bulk_update(batch, ["embedding"])
            summary["processed"] += len(batch)
        except Exception as exc:
            logger.exception("Embedding batch starting at chunk %d failed: %s", i, exc)
            summary["errors"] += len(batch)

    logger.info(
        "Document #%d embeddings done: %d processed, %d skipped, %d errors",
        document.pk, summary["processed"], summary["skipped"], summary["errors"]
    )
    return summary


def regenerate_all_embeddings(batch_size: int = 64, progress_callback=None) -> dict:
    """
    Regenerate dense BGE embeddings for all DocumentChunk records in memory-safe batches.
    """
    from apps.documents.models import DocumentChunk

    all_pks = list(DocumentChunk.objects.order_by("pk").values_list("pk", flat=True))
    total = len(all_pks)
    logger.info("Regenerating BGE embeddings for all %d DocumentChunk records...", total)
    summary = {"total": total, "processed": 0, "errors": 0}

    for i in range(0, total, batch_size):
        pk_batch = all_pks[i:i + batch_size]
        batch = list(DocumentChunk.objects.filter(pk__in=pk_batch).order_by("pk"))
        texts = [chunk.content for chunk in batch]
        try:
            vectors = embed_texts(texts)
            for chunk, vector in zip(batch, vectors):
                if len(vector) != EMBEDDING_DIMENSION:
                    raise ValueError(f"Embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {len(vector)}")
                chunk.embedding = vector
            DocumentChunk.objects.bulk_update(batch, ["embedding"])
            summary["processed"] += len(batch)
            if progress_callback:
                progress_callback(summary["processed"], total)
        except Exception as exc:
            logger.exception("Batch starting at index %d failed: %s", i, exc)
            summary["errors"] += len(batch)

    return summary


