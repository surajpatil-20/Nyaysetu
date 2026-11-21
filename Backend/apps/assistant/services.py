"""
NYAYASETU Assistant Service

Orchestrates evidence retrieval and grounded synthesis:
  1. Identify targeted Supreme Court case (citations, parties, coram, context).
  2. Retrieve relevant evidence chunks via case-aware Hybrid Search.
  3. Verify evidence sufficiency.
  4. Synthesize response through LLM provider.
  5. Attach verifiable source citations, identified precedent metadata, and mandatory disclaimer.
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
from apps.assistant.case_identifier import resolve_case_reference

logger = logging.getLogger(__name__)

# Minimum hybrid score threshold to consider an excerpt meaningful evidence
MIN_EVIDENCE_SCORE_THRESHOLD = 0.05


class AssistantService:
    @staticmethod
    def answer_question(
        query: str,
        case_id: Optional[int] = None,
        filters: Optional[dict] = None,
        top_k: int = 5,
        alpha: float = 0.5,
    ) -> dict:
        """
        Process a legal inquiry and return an evidence-grounded answer.

        Args:
            query: Citizen natural language question.
            case_id: Optional ID of active case for conversational continuity.
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
                "identified_case": Optional[dict],
                "needs_clarification": bool,
                "candidate_cases": list[dict],
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
                "identified_case": None,
                "needs_clarification": False,
                "candidate_cases": [],
            }

        # Step 0: Case Identification
        resolution = resolve_case_reference(query=query_clean, context_case_id=case_id)

        # Handle ambiguous case references (e.g. "Tell me about Union of India")
        if resolution.status == "AMBIGUOUS":
            candidate_list = []
            for c in resolution.candidate_cases:
                judges = [cj.judge.name for cj in c.case_judges.all()]
                candidate_list.append({
                    "id": c.id,
                    "case_number": c.case_number,
                    "case_title": c.case_title,
                    "decision_date": str(c.decision_date) if c.decision_date else None,
                    "court_name": c.court.court_name if c.court else "Supreme Court of India",
                    "bench": ", ".join(judges) if judges else "",
                    "relevance_reason": getattr(c, "relevance_reason", ""),
                })

            return {
                "query": query_clean,
                "answer": resolution.clarification_message,
                "has_sufficient_evidence": True,
                "evidence_count": 0,
                "sources": [],
                "disclaimer": DISCLAIMER_TEXT,
                "identified_case": None,
                "needs_clarification": True,
                "candidate_cases": candidate_list,
            }

        target_case = resolution.identified_case if resolution.status == "IDENTIFIED" else None
        search_filters = dict(filters or {})

        if target_case:
            search_filters["case_id"] = target_case.id

        # Step 1: Evidence Retrieval via Hybrid Search
        try:
            evidence_results: list[EvidenceResult] = hybrid_search(
                query=query_clean,
                filters=search_filters,
                top_k=top_k,
                alpha=alpha,
            )
        except Exception as exc:
            logger.exception("Hybrid search error during assistant processing: %s", exc)
            evidence_results = []

        # If a specific case is targeted, ensure the opening / headnote chunk (chunk_index=0) is available
        # so coram, date, appeal number, and headnote ratio are always grounded in official record
        if target_case:
            try:
                from apps.documents.models import DocumentChunk
                chunk0 = DocumentChunk.objects.filter(document__case=target_case, chunk_index=0).first()
                if chunk0 and not any(ev.chunk_id == chunk0.pk for ev in evidence_results):
                    doc = chunk0.document
                    headnote_ev = EvidenceResult(
                        chunk_id=chunk0.pk,
                        case_id=target_case.pk,
                        case_number=target_case.case_number,
                        case_title=target_case.case_title,
                        document_id=doc.pk,
                        document_title=doc.title,
                        document_type=doc.document_type,
                        page_number=chunk0.page_number,
                        snippet=chunk0.content[:300].strip(),
                        keyword_score=1.0,
                        semantic_score=1.0,
                        hybrid_score=1.0,
                        source_name=doc.source_name or target_case.source_name,
                        source_url=doc.source_url or target_case.source_url,
                        full_content=chunk0.content or "",
                    )
                    evidence_results.insert(0, headnote_ev)
            except Exception as exc:
                logger.warning("Could not append chunk0 for identified case: %s", exc)

        # Filter out results with negligible relevance score
        valid_evidence = [
            ev for ev in evidence_results
            if ev.hybrid_score >= MIN_EVIDENCE_SCORE_THRESHOLD
        ]

        identified_case_data = None
        if target_case:
            judges_list = [cj.judge.name for cj in target_case.case_judges.all()]
            identified_case_data = {
                "id": target_case.id,
                "case_number": target_case.case_number,
                "case_title": target_case.case_title,
                "decision_date": str(target_case.decision_date) if target_case.decision_date else None,
                "court_name": target_case.court.court_name if target_case.court else "Supreme Court of India",
                "bench": ", ".join(judges_list) if judges_list else "",
                "relevance_reason": resolution.match_reason,
            }

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
                "identified_case": identified_case_data,
                "needs_clarification": False,
                "candidate_cases": [],
            }

        # Step 2.5: Enrich evidence with Case / Court / Bench metadata
        case_ids = {getattr(ev, "case_id", None) for ev in valid_evidence if getattr(ev, "case_id", None)}
        cases_by_id = {}
        if case_ids:
            try:
                from apps.cases.models import Case
                qs = Case.objects.filter(pk__in=case_ids).select_related("court").prefetch_related("case_judges__judge")
                cases_by_id = {c.pk: c for c in qs}
            except Exception as exc:
                logger.warning("Could not prefetch cases for evidence enrichment: %s", exc)

        for ev in valid_evidence:
            c = cases_by_id.get(getattr(ev, "case_id", None))
            if c:
                judges = [cj.judge.name for cj in c.case_judges.all()]
                ev.bench = ", ".join(judges) if judges else ""
                ev.court_name = c.court.court_name if c.court else "Supreme Court of India"
                ev.decision_date = str(c.decision_date) if c.decision_date else ""
            else:
                ev.bench = getattr(ev, "bench", "")
                ev.court_name = getattr(ev, "court_name", "Supreme Court of India")
                ev.decision_date = getattr(ev, "decision_date", "")

        # Step 3: Prompt Construction & LLM Generation
        rag_prompt = build_rag_prompt(query_clean, valid_evidence)
        llm = get_llm_provider()

        try:
            answer = llm.generate(system_prompt=SYSTEM_PROMPT, user_prompt=rag_prompt)
        except Exception as exc:
            logger.exception("LLM generation failed for query '%s': %s", query_clean, exc)
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
                "court_name": getattr(ev, "court_name", "Supreme Court of India"),
                "bench": getattr(ev, "bench", ""),
                "decision_date": getattr(ev, "decision_date", ""),
            })

        return {
            "query": query_clean,
            "answer": answer,
            "has_sufficient_evidence": True,
            "evidence_count": len(sources),
            "sources": sources,
            "disclaimer": DISCLAIMER_TEXT,
            "identified_case": identified_case_data,
            "needs_clarification": False,
            "candidate_cases": [],
        }
