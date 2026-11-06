"""
NYAYASETU Assistant — Prompts and Guidance Instructions

Strict evidence-oriented judicial assistant system prompts.
Enforces that the AI behaves purely as an informational retrieval and synthesis layer.
"""

SYSTEM_PROMPT = """You are NYAYASETU, an AI-Assisted, Evidence-Oriented Judicial Information Assistant.

CORE MANDATE & OPERATING PRINCIPLES:
1. Grounding in Evidence: You must synthesize and explain legal information STRICTLY based on the provided judicial evidence excerpts. Do NOT hallucinate, extrapolate, or invent cases, laws, court rulings, or statutory sections.
2. What You Are NOT:
   - You are NOT a lawyer or advocate.
   - You do NOT give legal advice, strategy, or counsel.
   - You are NOT a judge and make no judicial determinations.
   - You do NOT predict case outcomes, judgment probabilities, or judge behaviors.
3. Insufficient Evidence Rule: If the provided evidence excerpts do not contain enough factual or legal basis to address the user's question, you MUST explicitly state that there is insufficient evidence in the NYAYASETU repository to answer the query. Do NOT speculate or rely on unverified outside knowledge.
4. Attribution & Citations: Whenever you state a legal principle, procedural development, or factual finding, cite the corresponding evidence item using its marker (e.g., [Evidence 1], [Evidence 2]) specifying the case name, court, document type, and page number if available.
5. Neutral & Objective Tone: Maintain an impartial, analytical, and respectful judicial tone.

OUTPUT FORMAT:
- Summary / Direct Information: A clear, objective explanation answering the question based solely on the retrieved evidence.
- Cited Points: Bulleted breakdown referencing specific [Evidence N] sources.
- Insufficient Evidence Notice: If evidence is missing or partial, clearly note what aspects cannot be answered.
"""

DISCLAIMER_TEXT = (
    "Disclaimer: NYAYASETU is an AI-assisted judicial information tool designed for citizen awareness "
    "and research. It does not provide legal advice, legal opinions, case outcome forecasts, or lawyer "
    "representation. For legal disputes or formal proceedings, consult a qualified advocate or the official "
    "court registry."
)

INSUFFICIENT_EVIDENCE_MESSAGE = (
    "There is insufficient judicial evidence in the NYAYASETU repository to answer this query reliably. "
    "Please refine your search keywords or verify against official court records."
)


def build_evidence_context(evidence_items: list) -> str:
    """
    Format a list of EvidenceResult objects or dicts into a structured context string for the prompt.
    """
    if not evidence_items:
        return "No judicial evidence excerpts available."

    lines = []
    for idx, ev in enumerate(evidence_items, start=1):
        # Support either EvidenceResult dataclass or dict
        if hasattr(ev, "case_number"):
            c_num = ev.case_number
            c_title = ev.case_title
            doc_title = ev.document_title
            page = f"Page {ev.page_number}" if ev.page_number else "Page N/A"
            source = ev.source_name or "Official/Verified Repository"
            snippet = ev.snippet
        else:
            c_num = ev.get("case_number", "N/A")
            c_title = ev.get("case_title", "N/A")
            doc_title = ev.get("document_title", "N/A")
            page = f"Page {ev.get('page_number')}" if ev.get("page_number") else "Page N/A"
            source = ev.get("source_name") or "Official/Verified Repository"
            snippet = ev.get("snippet", "")

        lines.append(
            f"--- [Evidence {idx}] ---\n"
            f"Case: {c_title} ({c_num})\n"
            f"Document: {doc_title} | {page} | Source: {source}\n"
            f"Excerpt:\n{snippet.strip()}\n"
        )

    return "\n".join(lines)


def build_rag_prompt(query: str, evidence_items: list) -> str:
    """
    Construct the complete user prompt incorporating query and retrieved context.
    """
    context = build_evidence_context(evidence_items)
    return (
        f"USER QUESTION: {query}\n\n"
        f"RETRIEVED JUDICIAL EVIDENCE EXCERPTS:\n"
        f"{context}\n\n"
        f"INSTRUCTIONS FOR YOUR RESPONSE:\n"
        f"1. Explain what the retrieved judicial evidence says regarding the question.\n"
        f"2. Reference the relevant [Evidence N] tags clearly.\n"
        f"3. If the excerpts do not address the question, clearly state: \"{INSUFFICIENT_EVIDENCE_MESSAGE}\"\n"
        f"4. Do NOT give legal advice or predict outcomes.\n"
    )

