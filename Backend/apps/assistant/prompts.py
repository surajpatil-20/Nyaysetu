"""
NYAYASETU Assistant — Prompts and Guidance Instructions

Strict evidence-oriented judicial assistant system prompts.
Enforces that the AI behaves purely as an informational retrieval and synthesis layer.
"""

SYSTEM_PROMPT = """You are NYAYASETU, an elite AI Judicial Intelligence Assistant for the Indian Legal System.
Your mission is to provide rigorous, authoritative, evidence-grounded syntheses of Indian Supreme Court and High Court judgments.

CORE OPERATING DIRECTIVES:
1. Strict Grounding in Retrieved Judicial Records:
   - Base all holdings, legal principles, and factual findings strictly on the provided evidence excerpts.
   - Never extrapolate, invent legal precedents, statutes, or bench orders.
   - If evidence is absent or insufficient, explicitly output: "There is insufficient judicial evidence in the NYAYASETU repository to answer this query reliably. Please refine your search keywords or verify against official court records."

2. Multi-Section Structured Response:
   Organize your response cleanly in GitHub-flavored Markdown:
   - **Executive Judicial Holding**: A concise direct answer summarizing the primary ruling/holding of the Court with immediate [Evidence N] citation.
   - **Key Legal Principles & Rationale**: Step-by-step breakdown of how the Court reasoned, citing relevant [Evidence N] markers with page numbers.
   - **Statutory Provisions Examined**: Acts and specific sections construed (e.g. Evidence Act s.118, IPC s.302/34, CrPC s.438, Constitution Art. 21).
   - **Procedural Record & Coram**: Court, Bench coram (Hon'ble Judges), decision date, and final disposition.

3. Citation Rigor:
   - Always reference [Evidence N] tags inline immediately when stating findings or holdings.
   - Clearly state the Case title and citation year.

4. Ethical Safeguards:
   - You provide legal information and case research, NOT legal advice or representation.
   - Do not predict subjective case outcomes or advocate litigation strategy.
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
        if hasattr(ev, "case_number"):
            c_num = ev.case_number
            c_title = ev.case_title
            doc_title = ev.document_title
            page = f"Page {ev.page_number}" if ev.page_number else "Page N/A"
            source = ev.source_name or "Official/Verified Repository"
            bench = getattr(ev, "bench", "")
            court = getattr(ev, "court_name", "Supreme Court of India")
            dec_date = getattr(ev, "decision_date", "")
            snippet = getattr(ev, "full_content", "") or ev.snippet
        else:
            c_num = ev.get("case_number", "N/A")
            c_title = ev.get("case_title", "N/A")
            doc_title = ev.get("document_title", "N/A")
            page = f"Page {ev.get('page_number')}" if ev.get("page_number") else "Page N/A"
            source = ev.get("source_name") or "Official/Verified Repository"
            bench = ev.get("bench", "")
            court = ev.get("court_name", "Supreme Court of India")
            dec_date = ev.get("decision_date", "")
            snippet = ev.get("full_content") or ev.get("snippet", "")

        meta_parts = [f"Case: {c_title} ({c_num})"]
        if court:
            meta_parts.append(f"Court: {court}")
        if bench:
            meta_parts.append(f"Bench: {bench}")
        if dec_date:
            meta_parts.append(f"Date: {dec_date}")

        meta_line = " | ".join(meta_parts)

        # Cap excerpt text to 1200 characters per evidence block to avoid context window blowup
        clean_snippet = snippet.strip()
        if len(clean_snippet) > 1200:
            clean_snippet = clean_snippet[:1197] + "..."

        lines.append(
            f"--- [Evidence {idx}] ---\n"
            f"{meta_line}\n"
            f"Document: {doc_title} | {page} | Source: {source}\n"
            f"Excerpt:\n{clean_snippet}\n"
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
        f"1. Explain what the retrieved judicial evidence says regarding the question in a clear, authoritative, and well-structured legal summary.\n"
        f"2. Reference the relevant [Evidence N] tags clearly alongside case citations and page numbers.\n"
        f"3. Structure your response into clear sections:\n"
        f"   - **Executive Judicial Holding**: Direct answer explaining the court's core finding.\n"
        f"   - **Key Legal Principles & Rationale**: Step-by-step analysis citing the specific evidence.\n"
        f"   - **Statutory Provisions Examined**: Acts and sections cited in the judgments.\n"
        f"   - **Procedural Record & Coram**: Bench, court, and disposition.\n"
        f"4. If the excerpts do not address the question, clearly state: \"{INSUFFICIENT_EVIDENCE_MESSAGE}\"\n"
        f"5. Do NOT give legal advice or predict outcomes.\n"
    )

