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
from dataclasses import dataclass, field
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
    matched_pages: list[int] = field(default_factory=list)
    matched_chunks_count: int = 1
    supporting_snippets: list[dict] = field(default_factory=list)


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
    'does', 'do', 'can', 'could', 'should', 'would', 'will', 'have', 'has', 'had',
    'versus', 'another', 'ors', 'etc'
}

MIN_HYBRID_THRESHOLD = 0.38
SEMANTIC_ONLY_THRESHOLD = 0.74


def _keyword_search(query: str, filters: dict, limit: int = 50) -> list:
    """
    Keyword search prioritizing exact Case metadata (citations, titles, party names)
    combined with term-coverage-weighted DocumentChunk content search.
    
    Guarantees:
    - Multi-word queries require minimum distinct term coverage (prevents spurious 1-word hits).
    - Case metadata matches receive top priority.
    - Absolute bounded scoring [0.0, 1.0] without artificial relative normalization.
    """
    from apps.cases.models import Case
    from apps.documents.models import DocumentChunk

    raw_tokens = re.findall(r'\b[a-zA-Z0-9]{2,}\b', query.lower())
    terms = [t for t in raw_tokens if t not in STOP_WORDS]
    if not terms:
        terms = raw_tokens
    if not terms:
        return []

    results = []
    seen_chunk_ids = set()

    # 1. Direct Case Metadata Search (Citation, Title, Party Names)
    meta_case_qs = Case.objects.exclude(source_name="DEMO SOURCE")
    if filters.get("court_id"):
        meta_case_qs = meta_case_qs.filter(court_id=filters["court_id"])
    if filters.get("case_type"):
        meta_case_qs = meta_case_qs.filter(case_type__icontains=filters["case_type"])
    if filters.get("year"):
        meta_case_qs = meta_case_qs.filter(
            Q(filing_date__year=filters["year"]) | Q(decision_date__year=filters["year"])
        )
    if filters.get("case_id"):
        meta_case_qs = meta_case_qs.filter(pk=filters["case_id"])

    exact_q_lower = query.lower().strip()
    meta_matches = []  # (case_id, score)

    for case_obj in meta_case_qs:
        c_title = (case_obj.case_title or "").lower()
        c_num = (case_obj.case_number or "").lower()
        combined_meta = f"{c_num} {c_title}"

        # Exact phrase in citation or title
        if exact_q_lower in combined_meta:
            meta_matches.append((case_obj.id, 1.0))
        # All non-stopword query terms present in citation or title
        elif all(t in combined_meta for t in terms):
            meta_matches.append((case_obj.id, 1.0))
        # For queries with 3+ terms, almost all terms present
        elif len(terms) >= 3 and sum(1 for t in terms if t in combined_meta) >= len(terms) - 1:
            coverage = sum(1 for t in terms if t in combined_meta) / len(terms)
            meta_matches.append((case_obj.id, round(0.85 * coverage, 4)))

    if meta_matches:
        # Fetch chunks for metadata-matched cases
        matched_case_ids = [cid for cid, _ in meta_matches]
        score_by_case = dict(meta_matches)
        meta_chunks = DocumentChunk.objects.filter(
            document__case_id__in=matched_case_ids
        ).select_related(
            "document", "document__case", "document__case__court"
        ).order_by("chunk_index")

        if filters.get("document_type"):
            meta_chunks = meta_chunks.filter(document__document_type=filters["document_type"])

        # Limit to top chunks per matched case
        chunks_per_case: dict[int, int] = {}
        for chunk in meta_chunks[:limit]:
            cid = chunk.document.case_id
            chunks_per_case[cid] = chunks_per_case.get(cid, 0) + 1
            if chunks_per_case[cid] <= 5:
                results.append((chunk, score_by_case.get(cid, 0.95)))
                seen_chunk_ids.add(chunk.id)

    # 2. Content Search in DocumentChunks with Term-Coverage Scoring
    min_distinct = len(terms) if len(terms) <= 2 else math.ceil(len(terms) * 0.6)

    chunk_q = Q()
    for term in terms:
        chunk_q |= Q(content__icontains=term)

    content_qs = DocumentChunk.objects.select_related(
        "document", "document__case", "document__case__court"
    ).filter(chunk_q).exclude(
        document__case__source_name="DEMO SOURCE"
    ).exclude(
        document__source_name="DEMO SOURCE"
    )

    if filters.get("case_id"):
        content_qs = content_qs.filter(document__case_id=filters["case_id"])
    if filters.get("court_id"):
        content_qs = content_qs.filter(document__case__court_id=filters["court_id"])
    if filters.get("case_type"):
        content_qs = content_qs.filter(document__case__case_type__icontains=filters["case_type"])
    if filters.get("year"):
        content_qs = content_qs.filter(
            Q(document__case__filing_date__year=filters["year"]) |
            Q(document__case__decision_date__year=filters["year"])
        )
    if filters.get("document_type"):
        content_qs = content_qs.filter(document__document_type=filters["document_type"])

    fetch_chunk_limit = max(limit * 3, 100)
    for chunk in content_qs[:fetch_chunk_limit]:
        if chunk.id in seen_chunk_ids:
            continue

        content_lower = chunk.content.lower()
        title_lower = (chunk.document.case.case_title or "").lower() if chunk.document and chunk.document.case else ""
        num_lower = (chunk.document.case.case_number or "").lower() if chunk.document and chunk.document.case else ""
        text_to_match = f"{content_lower} {title_lower} {num_lower}"

        distinct_matches = sum(1 for t in terms if t in text_to_match)
        # Multi-term queries require minimum distinct term coverage
        if distinct_matches < min_distinct:
            continue

        matches = sum(text_to_match.count(t) for t in terms)
        coverage_ratio = distinct_matches / len(terms)

        # Absolute bounded keyword score: coverage weight + term frequency log bonus
        base_score = 0.70 * coverage_ratio
        freq_bonus = min(0.15, 0.05 * math.log1p(matches))
        meta_bonus = 0.10 if any(t in title_lower or t in num_lower for t in terms) else 0.0
        score = min(0.95, base_score + freq_bonus + meta_bonus)

        if score >= 0.40:
            results.append((chunk, score))
            seen_chunk_ids.add(chunk.id)

    return results


def _semantic_vector_search(query_vector: list[float], filters: dict, top_k: int) -> list:
    """
    Semantic vector retrieval performed entirely inside PostgreSQL using pgvector CosineDistance.
    Retrieves only the top_k rows ordered by cosine distance directly from the database.
    """
    from apps.documents.models import DocumentChunk

    qs = DocumentChunk.objects.select_related(
        "document", "document__case", "document__case__court"
    ).filter(embedding__isnull=False).exclude(
        document__case__source_name="DEMO SOURCE"
    ).exclude(
        document__source_name="DEMO SOURCE"
    ).annotate(
        distance=CosineDistance("embedding", query_vector)
    )

    # Apply optional filters
    if filters.get("case_id"):
        qs = qs.filter(document__case_id=filters["case_id"])
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
        # When filtered to a specific case_id, allow broader distance threshold (0.65).
        max_dist = 0.65 if filters.get("case_id") else 0.38
        dist = float(chunk.distance) if chunk.distance is not None else 1.0
        if dist > max_dist:
            continue
        similarity = max(0.0, 1.0 - dist)
        results.append((chunk, similarity))

    return results


def group_results_by_case(
    evidence_list: list[EvidenceResult],
    max_cases: Optional[int] = None,
) -> list[EvidenceResult]:
    """
    Groups a list of chunk-level EvidenceResult objects by unique case_id.

    - Uses the chunk with the highest hybrid_score as the primary snippet and score.
    - Aggregates unique page numbers into `matched_pages` (sorted).
    - Counts total matching chunks in `matched_chunks_count`.
    - Captures other relevant page snippets into `supporting_snippets`.
    - Orders the unique cases by highest hybrid_score descending.
    """
    if not evidence_list:
        return []

    groups: dict[int, list[EvidenceResult]] = {}
    for ev in evidence_list:
        cid = ev.case_id
        if cid not in groups:
            groups[cid] = []
        groups[cid].append(ev)

    grouped: list[EvidenceResult] = []
    for cid, chunks in groups.items():
        # Sort chunks by hybrid_score descending so highest relevance is primary
        chunks.sort(key=lambda x: x.hybrid_score, reverse=True)
        best = chunks[0]

        pages = sorted({c.page_number for c in chunks if c.page_number is not None})
        if not pages and best.page_number is not None:
            pages = [best.page_number]

        supporting = []
        seen_snippets = {best.snippet.strip()}
        for other in chunks[1:]:
            s_clean = other.snippet.strip()
            if s_clean and s_clean not in seen_snippets:
                seen_snippets.add(s_clean)
                supporting.append({
                    "chunk_id": other.chunk_id,
                    "page_number": other.page_number,
                    "snippet": other.snippet,
                    "score": other.hybrid_score,
                })

        grouped_case = EvidenceResult(
            chunk_id=best.chunk_id,
            case_id=best.case_id,
            case_number=best.case_number,
            case_title=best.case_title,
            document_id=best.document_id,
            document_title=best.document_title,
            document_type=best.document_type,
            page_number=best.page_number,
            snippet=best.snippet,
            keyword_score=best.keyword_score,
            semantic_score=best.semantic_score,
            hybrid_score=best.hybrid_score,
            source_name=best.source_name,
            source_url=best.source_url,
            full_content=best.full_content,
            matched_pages=pages,
            matched_chunks_count=len(chunks),
            supporting_snippets=supporting[:5],
        )
        grouped.append(grouped_case)

    # Sort grouped cases by best hybrid_score descending
    grouped.sort(key=lambda x: x.hybrid_score, reverse=True)

    if max_cases is not None:
        grouped = grouped[:max_cases]

    return grouped


def hybrid_search(
    query: str,
    filters: Optional[dict] = None,
    top_k: int = MAX_RESULTS,
    alpha: float = ALPHA,
    group_by_case: bool = False,
) -> list[EvidenceResult]:
    """
    Main hybrid search function.

    Combines:
      - Keyword search: PostgreSQL ILIKE with term coverage scoring
      - Semantic search: PostgreSQL pgvector CosineDistance ordering

    Formula:
      hybrid_score = α * keyword_score + (1 - α) * semantic_score

    If `group_by_case` is True, results are grouped by unique case_id so each
    case is represented once with its highest-scoring chunk and aggregated pages.
    """
    if not query or not query.strip():
        return []

    filters = filters or {}
    candidate_chunks: dict[int, object] = {}
    keyword_scores: dict[int, float] = {}
    semantic_scores: dict[int, float] = {}

    # Step 1: Keyword Search
    fetch_limit = top_k * 5 if group_by_case else top_k * 3
    if alpha > 0.0:
        keyword_hits = _keyword_search(query, filters, limit=fetch_limit)
        for chunk, k_score in keyword_hits:
            candidate_chunks[chunk.pk] = chunk
            keyword_scores[chunk.pk] = k_score

    # Step 2: PostgreSQL pgvector Semantic Search
    if alpha < 1.0:
        try:
            from apps.documents.services.embeddings import embed_single
            query_vector = embed_single(query)

            vector_hits = _semantic_vector_search(query_vector, filters, top_k=fetch_limit)
            for chunk, s_score in vector_hits:
                candidate_chunks[chunk.pk] = chunk
                semantic_scores[chunk.pk] = s_score
        except Exception as exc:
            logger.warning("PostgreSQL pgvector search failed, using keyword search only: %s", exc)

    # Step 3: Score Fusion and Relevance Filtering
    all_pks = set(candidate_chunks.keys())
    if not all_pks:
        return []

    fused: list[tuple[float, int]] = []
    is_pinned_case = bool(filters.get("case_id"))

    for pk in all_pks:
        ks = keyword_scores.get(pk, 0.0)
        ss = semantic_scores.get(pk, 0.0)

        # Relevance Confidence Guard:
        # If the chunk has NO keyword matches (semantic-only), require a strict semantic threshold
        # to prevent nearest-neighbor vector drift from returning random cases on unrelated queries.
        if ks == 0.0 and not is_pinned_case and ss < SEMANTIC_ONLY_THRESHOLD:
            continue

        hybrid = (alpha * ks) + ((1.0 - alpha) * ss)

        # Enforce minimum relevance/confidence threshold
        if not is_pinned_case and hybrid < MIN_HYBRID_THRESHOLD:
            continue
        elif is_pinned_case and hybrid <= 0.0:
            continue

        fused.append((hybrid, pk))

    if not fused:
        return []

    fused.sort(reverse=True)
    candidate_limit = max(top_k * 5, 100) if group_by_case else top_k
    top = fused[:candidate_limit]

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
        p_num = chunk.page_number
        results.append(EvidenceResult(
            chunk_id=chunk.pk,
            case_id=case.pk,
            case_number=case.case_number,
            case_title=case.case_title,
            document_id=doc.pk,
            document_title=doc.title,
            document_type=doc.document_type,
            page_number=p_num,
            snippet=_snippet(chunk.content, query),
            keyword_score=round(keyword_scores.get(pk, 0.0), 4),
            semantic_score=round(semantic_scores.get(pk, 0.0), 4),
            hybrid_score=round(hybrid_score, 4),
            source_name=doc.source_name or (case.source_name if case else None),
            source_url=doc.source_url or (case.source_url if case else None),
            full_content=chunk.content or "",
            matched_pages=[p_num] if p_num is not None else [],
            matched_chunks_count=1,
            supporting_snippets=[],
        ))

    if group_by_case:
        return group_results_by_case(results, max_cases=top_k)

    return results
