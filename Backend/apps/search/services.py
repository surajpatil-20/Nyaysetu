"""
NYAYASETU Hybrid Search Service

Combines PostgreSQL keyword search and PostgreSQL pgvector semantic vector search.

Architecture:
  1. Keyword Search: PostgreSQL ILIKE on content + case fields with term-coverage weighting.
  2. Semantic Search: Database-side pgvector CosineDistance query using HNSW index.
     - Embeds query into 768-dim dense vector.
     - Executes: DocumentChunk.objects.annotate(distance=CosineDistance('embedding', query_vector)).order_by('distance')[:top_k]
     - Evaluated entirely within PostgreSQL; does NOT load all embeddings into Python memory.
  3. Score Fusion: hybrid_score = α * keyword_score + (1 - α) * semantic_score
  4. Returns EvidenceResult objects with complete provenance.
"""
import logging
import math
import re
from dataclasses import dataclass
from typing import Optional

from django.db.models import Q
from pgvector.django import CosineDistance

logger = logging.getLogger(__name__)

ALPHA = 0.5          # Default keyword weight (0.5 = balanced keyword and vector search)
MAX_RESULTS = 20      # Default max results returned


@dataclass
class EvidenceResult:
    chunk_id: int
    case_id: int
    case_number: str
    case_title: str
    document_id: int
    document_title: str
    document_type: str
    page_number: Optional[int]
    snippet: str
    keyword_score: float
    semantic_score: float
    hybrid_score: float
    source_name: Optional[str]
    source_url: Optional[str]
    full_content: str = ""


def _snippet(text: str, query: str, max_len: int = 300) -> str:
    """Extract a relevant snippet around the query terms."""
    text_lower = text.lower()
    query_lower = query.lower()
    words = query_lower.split()

    best_pos = 0
    for word in words:
        pos = text_lower.find(word)
        if pos >= 0:
            best_pos = max(0, pos - 100)
            break

    snippet = text[best_pos:best_pos + max_len]
    if best_pos > 0:
        snippet = "…" + snippet
    if best_pos + max_len < len(text):
        snippet = snippet + "…"
    return snippet.strip()


# Common English legal search stop words
STOP_WORDS = {
    'what', 'did', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'and', 'or', 'regarding', 'about', 'how', 'why', 'when', 'where',
    'who', 'which', 'by', 'from', 'an', 'a', 'this', 'that', 'these', 'those', 'it',
    'does', 'do', 'can', 'could', 'should', 'would', 'will', 'have', 'has', 'had'
}


def _keyword_search(query: str, filters: dict, limit: int = 50) -> list:
    """
    Keyword search over DocumentChunk.content.
    Extracts alphanumeric tokens, excludes common stop words, and matches
    with OR semantics and term-coverage scoring.
    """
    from apps.documents.models import DocumentChunk

    raw_tokens = re.findall(r'\b[a-zA-Z0-9]{2,}\b', query.lower())
    terms = [t for t in raw_tokens if t not in STOP_WORDS]
    if not terms:
        terms = raw_tokens
    if not terms:
        return []

    q = Q()
    for term in terms:
        q |= (
            Q(content__icontains=term) |
            Q(document__case__case_title__icontains=term) |
            Q(document__case__case_number__icontains=term)
        )

    qs = DocumentChunk.objects.select_related(
        "document", "document__case", "document__case__court"
    ).filter(q)

    # Apply optional filters
    if filters.get("court_id"):
        qs = qs.filter(document__case__court_id=filters["court_id"])
    if filters.get("case_type"):
        qs = qs.filter(document__case__case_type__icontains=filters["case_type"])
    if filters.get("year"):
        qs = qs.filter(
            Q(document__case__filing_date__year=filters["year"]) |
            Q(document__case__decision_date__year=filters["year"])
        )
    if filters.get("document_type"):
        qs = qs.filter(document__document_type=filters["document_type"])

    qs = qs[:limit]
    results = []
    for chunk in qs:
        content_lower = chunk.content.lower()
        title_lower = (chunk.document.case.case_title or "").lower() if chunk.document and chunk.document.case else ""
        num_lower = (chunk.document.case.case_number or "").lower() if chunk.document and chunk.document.case else ""
        text_to_match = f"{content_lower} {title_lower} {num_lower}"
        matches = sum(text_to_match.count(t) for t in terms)
        distinct_matches = sum(1 for t in terms if t in text_to_match)
        # Avoid spurious single-term matches on multi-term queries
        if len(terms) >= 3 and distinct_matches < 2:
            continue
        coverage_ratio = distinct_matches / max(len(terms), 1)
        score = math.log1p(matches) * (1.0 + coverage_ratio)
        if score > 0:
            results.append((chunk, score))

    if results:
        max_score = max(s for _, s in results) or 1.0
        results = [(c, s / max_score) for c, s in results]

    return results


def _semantic_vector_search(query_vector: list[float], filters: dict, top_k: int) -> list:
    """
    Semantic vector retrieval performed entirely inside PostgreSQL using pgvector CosineDistance.
    Retrieves only the top_k rows ordered by cosine distance directly from the database.
    """
    from apps.documents.models import DocumentChunk

    qs = DocumentChunk.objects.select_related(
        "document", "document__case", "document__case__court"
    ).filter(embedding__isnull=False).annotate(
        distance=CosineDistance("embedding", query_vector)
    )

    # Apply optional filters
    if filters.get("court_id"):
        qs = qs.filter(document__case__court_id=filters["court_id"])
    if filters.get("case_type"):
        qs = qs.filter(document__case__case_type__icontains=filters["case_type"])
    if filters.get("year"):
        qs = qs.filter(
            Q(document__case__filing_date__year=filters["year"]) |
            Q(document__case__decision_date__year=filters["year"])
        )
    if filters.get("document_type"):
        qs = qs.filter(document__document_type=filters["document_type"])

    # Push top-k ordering to PostgreSQL (HNSW index accelerated)
    qs = qs.order_by("distance")[:top_k]

    results = []
    for chunk in qs:
        # Distance is in [0, 2]. Distance <= 0 means identical; 1 means orthogonal.
        # Chunks with cosine distance > 0.38 have low semantic correlation and are discarded.
        dist = float(chunk.distance) if chunk.distance is not None else 1.0
        if dist > 0.38:
            continue
        similarity = max(0.0, 1.0 - dist)
        results.append((chunk, similarity))

    return results


def hybrid_search(
    query: str,
    filters: Optional[dict] = None,
    top_k: int = MAX_RESULTS,
    alpha: float = ALPHA,
) -> list[EvidenceResult]:
    """
    Main hybrid search function.

    Combines:
      - Keyword search: PostgreSQL ILIKE with term coverage scoring
      - Semantic search: PostgreSQL pgvector CosineDistance ordering

    Formula:
      hybrid_score = α * keyword_score + (1 - α) * semantic_score
    """
    if not query or not query.strip():
        return []

    filters = filters or {}
    candidate_chunks: dict[int, object] = {}
    keyword_scores: dict[int, float] = {}
    semantic_scores: dict[int, float] = {}

    # Step 1: Keyword Search
    if alpha > 0.0:
        keyword_hits = _keyword_search(query, filters, limit=top_k * 3)
        for chunk, k_score in keyword_hits:
            candidate_chunks[chunk.pk] = chunk
            keyword_scores[chunk.pk] = k_score

    # Step 2: PostgreSQL pgvector Semantic Search
    if alpha < 1.0:
        try:
            from apps.documents.services.embeddings import embed_single
            query_vector = embed_single(query)

            vector_hits = _semantic_vector_search(query_vector, filters, top_k=top_k * 2)
            for chunk, s_score in vector_hits:
                candidate_chunks[chunk.pk] = chunk
                semantic_scores[chunk.pk] = s_score
        except Exception as exc:
            logger.warning("PostgreSQL pgvector search failed, using keyword search only: %s", exc)

    # Step 3: Score Fusion
    all_pks = set(candidate_chunks.keys())
    if not all_pks:
        return []

    fused: list[tuple[float, int]] = []
    for pk in all_pks:
        ks = keyword_scores.get(pk, 0.0)
        ss = semantic_scores.get(pk, 0.0)
        hybrid = (alpha * ks) + ((1.0 - alpha) * ss)
        fused.append((hybrid, pk))

    fused.sort(reverse=True)
    top = fused[:top_k]

    # Step 4: Build EvidenceResult objects
    results = []
    for hybrid_score, pk in top:
        if hybrid_score <= 0.0:
            continue
        chunk = candidate_chunks.get(pk)
        if chunk is None:
            continue
        doc = chunk.document
        case = doc.case
        results.append(EvidenceResult(
            chunk_id=chunk.pk,
            case_id=case.pk,
            case_number=case.case_number,
            case_title=case.case_title,
            document_id=doc.pk,
            document_title=doc.title,
            document_type=doc.document_type,
            page_number=chunk.page_number,
            snippet=_snippet(chunk.content, query),
            keyword_score=round(keyword_scores.get(pk, 0.0), 4),
            semantic_score=round(semantic_scores.get(pk, 0.0), 4),
            hybrid_score=round(hybrid_score, 4),
            source_name=doc.source_name or (case.source_name if case else None),
            source_url=doc.source_url or (case.source_url if case else None),
            full_content=chunk.content or "",
        ))

    return results
