"""
NYAYASETU Assistant Service

Orchestrates evidence retrieval and grounded synthesis:
  1. Retrieve relevant evidence chunks via Hybrid Search.
  2. Verify evidence sufficiency.
  3. Synthesize response through LLM provider.
  4. Attach verifiable source citations and mandatory disclaimer.
"""
import logging
from typing import Optional

from apps.search.services import hybrid_search, EvidenceResult
from apps.assistant.prompts import (
    SYSTEM_PROMPT,
    DISCLAIMER_TEXT,
    INSUFFICIENT_EVIDENCE_MESSAGE,
    build_rag_prompt,
)
from apps.assistant.llm import get_llm_provider

logger = logging.getLogger(__name__)

# Minimum hybrid score threshold to consider an excerpt meaningful evidence
MIN_EVIDENCE_SCORE_THRESHOLD = 0.05


class AssistantService:
    @staticmethod
    def answer_question(
        query: str,
        filters: Optional[dict] = None,
        top_k: int = 5,
        alpha: float = 0.5,
    ) -> dict:
        """
        Process a legal inquiry and return an evidence-grounded answer.

        Args:
            query: Citizen natural language question.
            filters: Optional search filters (court_id, case_type, year, document_type).
            top_k: Number of evidence chunks to retrieve for context.
            alpha: Search balance (0.5 = equal keyword and semantic weights).

        Returns:
            {
                "query": str,
                "answer": str,
                "has_sufficient_evidence": bool,
                "evidence_count": int,
                "sources": list[dict],
                "disclaimer": str,
            }
        """
        query_clean = query.strip()
        if not query_clean:
            return {
                "query": query,
                "answer": "Please provide a valid question or topic to search.",
                "has_sufficient_evidence": False,
                "evidence_count": 0,
                "sources": [],
                "disclaimer": DISCLAIMER_TEXT,
            }

        # Step 1: Evidence Retrieval via Hybrid Search
        try:
            evidence_results: list[EvidenceResult] = hybrid_search(
                query=query_clean,
                filters=filters or {},
                top_k=top_k,
                alpha=alpha,
            )
        except Exception as exc:
            logger.exception("Hybrid search error during assistant processing: %s", exc)
            evidence_results = []

        # Filter out results with negligible relevance score
        valid_evidence = [
            ev for ev in evidence_results
            if ev.hybrid_score >= MIN_EVIDENCE_SCORE_THRESHOLD
        ]

        # Step 2: Check Evidence Sufficiency
        if not valid_evidence:
            logger.info("Insufficient evidence retrieved for query: '%s'", query_clean)
            return {
                "query": query_clean,
                "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
                "has_sufficient_evidence": False,
                "evidence_count": 0,
                "sources": [],
                "disclaimer": DISCLAIMER_TEXT,
            }

        # Step 3: Prompt Construction & LLM Generation
        rag_prompt = build_rag_prompt(query_clean, valid_evidence)
        llm = get_llm_provider()

        try:
            answer = llm.generate(system_prompt=SYSTEM_PROMPT, user_prompt=rag_prompt)
        except Exception as exc:
            logger.exception("LLM generation failed for query '%s': %s", query_clean, exc)
            # Safe fallback if LLM service errors
            answer = (
                f"We retrieved relevant judicial records, but the AI synthesis service is temporarily "
                f"unavailable. Please review the cited source documents below directly.\n\n"
                f"Error details: {exc}"
            )

        # Step 4: Format Source Citations
        sources = []
        for idx, ev in enumerate(valid_evidence, start=1):
            sources.append({
                "citation_tag": f"[Evidence {idx}]",
                "chunk_id": ev.chunk_id,
                "case_id": ev.case_id,
                "case_number": ev.case_number,
                "case_title": ev.case_title,
                "document_id": ev.document_id,
                "document_title": ev.document_title,
                "document_type": ev.document_type,
                "page_number": ev.page_number,
                "snippet": ev.snippet,
                "relevance_score": ev.hybrid_score,
                "source_name": ev.source_name,
                "source_url": ev.source_url,
            })

        return {
            "query": query_clean,
            "answer": answer,
            "has_sufficient_evidence": True,
            "evidence_count": len(sources),
            "sources": sources,
            "disclaimer": DISCLAIMER_TEXT,
        }

