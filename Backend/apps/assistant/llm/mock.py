"""
NYAYASETU Intelligent Judicial Synthesizer (Mock LLM Provider).

Deterministic, grounded legal synthesizer for offline environments, CI/CD, and local development.
Parses Supreme Court / High Court judgment excerpts, extracts legal holdings, ratio decidendi,
statutory provisions, and coram, and structures an authoritative judicial brief.
"""
import re
from apps.assistant.llm.base import BaseLLMProvider
from apps.assistant.prompts import INSUFFICIENT_EVIDENCE_MESSAGE


def clean_ocr(text: str) -> str:
    """Strip OCR margins, SCR page headers, and normalize whitespace."""
    cleaned = re.sub(r'\b[A-H]\s+(?:\b[A-H]\s+)*', ' ', text)
    cleaned = re.sub(r'\[\d{4}\]\s+\d+\s+S\.C\.R\.[\s\d:]*', ' ', cleaned)
    cleaned = re.sub(r'\b\d{4}\s+SUPREME COURT REPORTS\b', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d{4}\s+INSC\s+\d+\b', ' ', cleaned)
    cleaned = re.sub(r'\b[0-9]{3,4}\s+A B C D E F G H\b', ' ', cleaned)
    # Strip leading judge bracket artifacts like [ABHAY S. OKA AND RAJESH BINDAL, JJ.]
    cleaned = re.sub(r'\[[A-Z\s,]+(?:JJ|J)\.?\]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def extract_statutes(text: str) -> tuple[list[str], list[str]]:
    """Extract Acts and Sections mentioned in the judicial text."""
    sections = []
    sec_matches = re.findall(
        r'(?:Section|Sec\.|ss?\.)\s*(\d+[A-Za-z]?(?:\s*(?:r/w|read with|/)\s*(?:ss?\.?|Section)?\s*\d+[A-Za-z]?)*(?:\s*,\s*\d+[A-Za-z]?)*)',
        text,
        flags=re.IGNORECASE
    )
    for m in sec_matches:
        s = m.strip()
        if len(s) < 25 and f"Section {s}" not in sections:
            sections.append(f"Section {s}")

    art_matches = re.findall(r'Article\s+(\d+[A-Za-z]?)', text, flags=re.IGNORECASE)
    for m in art_matches:
        s = f"Article {m.strip()}"
        if s not in sections:
            sections.append(s)

    acts = []
    if re.search(r'\bEvidence Act\b', text, flags=re.IGNORECASE):
        acts.append("Indian Evidence Act, 1872")
    if re.search(r'\b(?:IPC|Indian Penal Code)\b', text, flags=re.IGNORECASE):
        acts.append("Indian Penal Code, 1860")
    if re.search(r'\b(?:CrPC|Cr\.P\.C\.|Code of Criminal Procedure)\b', text, flags=re.IGNORECASE):
        acts.append("Code of Criminal Procedure, 1973")
    if re.search(r'\bOaths Act\b', text, flags=re.IGNORECASE):
        acts.append("Oaths Act, 1969")
    if re.search(r'\bConstitution\b', text, flags=re.IGNORECASE):
        acts.append("Constitution of India")

    return acts, sections[:6]


def split_sentences(text: str) -> list[str]:
    """Break cleaned text into coherent sentences."""
    raw = re.split(r'(?<=[.?!])\s+(?=[A-Z0-9“"\'\[])', text)
    sentences = []
    for s in raw:
        s = s.strip()
        # Exclude headers and very short noise fragments
        if len(s) >= 30 and not re.match(r'^(?:Page|Source|Document|---)', s):
            sentences.append(s)
    return sentences


class MockLLMProvider(BaseLLMProvider):
    """
    Intelligent Judicial Synthesizer that extracts holdings, ratios,
    and statutory references from retrieved judicial evidence.
    """

    OPERATIVE_WEIGHTS = {
        "held that": 15,
        "held:": 15,
        "sole basis of conviction": 16,
        "competent to depose": 14,
        "under section 118": 14,
        "preliminary examination": 12,
        "tutored": 14,
        "tutoring": 14,
        "corroboration": 12,
        "benefit of doubt": 14,
        "conviction is set aside": 16,
        "appeal is allowed": 16,
        "acquitted": 15,
        "care and caution": 12,
        "scrutiny of the evidence": 12,
        "equality before law": 14,
        "article 14": 14,
        "article 21": 14,
        "quashing of": 12,
        "anticipatory bail": 14,
    }

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # 1. Sufficiency checks
        if "No judicial evidence excerpts available." in user_prompt or "[Evidence 1]" not in user_prompt:
            return INSUFFICIENT_EVIDENCE_MESSAGE

        # 2. Extract user query
        query_match = re.search(r'USER QUESTION:\s*(.*?)\n\n', user_prompt, re.DOTALL)
        query = query_match.group(1).strip() if query_match else ""

        # 3. Extract Evidence blocks
        pattern = (
            r'--- \[Evidence (\d+)\] ---\s*'
            r'([^\n]+)\s*'
            r'Document:\s*([^\n]+)\s*'
            r'Excerpt:\s*(.*?)(?=(?:--- \[Evidence|\n+INSTRUCTIONS|$))'
        )
        blocks = re.findall(pattern, user_prompt, re.DOTALL)
        if not blocks:
            return INSUFFICIENT_EVIDENCE_MESSAGE

        parsed_evidence = []
        for num_str, meta_line, doc_line, excerpt in blocks:
            idx = int(num_str)
            # Parse metadata line: Case: ... | Court: ... | Bench: ... | Date: ...
            c_title = "Supreme Court Judgment"
            c_num = ""
            court = "Supreme Court of India"
            bench = ""
            date = ""

            case_match = re.search(r'Case:\s*(.+?)(?:\s*\(([^)]+)\))?(?:\s*\||$)', meta_line)
            if case_match:
                c_title = case_match.group(1).strip()
                if case_match.group(2):
                    c_num = case_match.group(2).strip()

            court_match = re.search(r'Court:\s*([^|]+)', meta_line)
            if court_match:
                court = court_match.group(1).strip()

            bench_match = re.search(r'Bench:\s*([^|]+)', meta_line)
            if bench_match:
                bench = bench_match.group(1).strip()

            date_match = re.search(r'Date:\s*([^|]+)', meta_line)
            if date_match:
                date = date_match.group(1).strip()

            # Parse page from doc_line
            page_match = re.search(r'Page\s+(\d+)', doc_line)
            page = int(page_match.group(1)) if page_match else None

            clean_text = clean_ocr(excerpt)
            parsed_evidence.append({
                "idx": idx,
                "case_title": c_title,
                "case_number": c_num,
                "court": court,
                "bench": bench,
                "date": date,
                "page": page,
                "doc_line": doc_line.strip(),
                "clean_text": clean_text,
            })

        # 4. Extract query keywords for scoring
        query_words = [
            w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', query)
            if w.lower() not in {"what", "held", "regarding", "the", "state", "case", "court"}
        ]

        # 5. Extract global statutes and acts across all excerpts
        combined_text = " ".join(e["clean_text"] for e in parsed_evidence)
        acts, sections = extract_statutes(combined_text)

        # 6. Score individual sentences across evidence blocks
        scored_sentences = []
        for ev in parsed_evidence:
            sentences = split_sentences(ev["clean_text"])
            for s in sentences:
                score = 0
                s_lower = s.lower()
                for w in query_words:
                    if w in s_lower:
                        score += 3
                for kw, weight in self.OPERATIVE_WEIGHTS.items():
                    if kw in s_lower:
                        score += weight

                if score > 0:
                    scored_sentences.append((score, ev["idx"], ev["page"], s))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        # 7. Identify primary case details
        first_ev = parsed_evidence[0]
        p_title = first_ev["case_title"]
        p_num = f" ({first_ev['case_number']})" if first_ev["case_number"] else ""
        p_court = first_ev["court"]
        p_bench = first_ev["bench"]
        p_date = first_ev["date"]

        # 8. Synthesize Executive Judicial Holding
        # Pick the most authoritative holding statement
        holding_sentence = None
        for sc, idx, pg, s in scored_sentences:
            if any(h in s.lower() for h in ["held that", "held:", "sole basis of conviction", "guarantees equality", "cannot be sustained"]):
                # Clean prefix: if 'Held:' is present, start from the text after 'Held:'
                if re.search(r'\bHeld\s*:\s*', s, flags=re.IGNORECASE):
                    clean_s = re.sub(r'^.*?\bHeld\s*:\s*', '', s, flags=re.IGNORECASE).strip()
                else:
                    clean_s = re.sub(r'^(?:Evidence\s*–\s*|[\d\s,./r/w\-IPC]+–\s*)', '', s, flags=re.IGNORECASE).strip()
                # Ensure starts with uppercase or clean letter
                clean_s = re.sub(r'^[^a-zA-Z"\'“]+', '', clean_s)
                if len(clean_s) > 350:
                    clean_s = clean_s[:347] + "..."
                holding_sentence = (idx, pg, clean_s)
                break

        if not holding_sentence and scored_sentences:
            holding_sentence = (scored_sentences[0][1], scored_sentences[0][2], scored_sentences[0][3])

        response_sections = []

        # SECTION 1: Executive Judicial Holding
        response_sections.append("### Executive Judicial Holding")
        if holding_sentence:
            idx, pg, sent = holding_sentence
            bench_str = f" (Bench of {p_bench})" if p_bench else ""
            response_sections.append(
                f"In **{p_title}{p_num}** [Evidence {idx}], the {p_court}{bench_str} held:\n\n"
                f"> \"{sent}\""
            )
        else:
            response_sections.append(
                f"In **{p_title}{p_num}** [Evidence 1], the {p_court} examined the judicial record regarding this inquiry."
            )

        # SECTION 2: Key Legal Principles & Ratio Decidendi
        response_sections.append("\n### Key Legal Principles & Ratio Decidendi")
        # Select up to 4 top unique propositions
        used_propositions = set()
        count = 0
        for sc, idx, pg, s in scored_sentences:
            if holding_sentence and s == holding_sentence[2]:
                continue
            # Deduplicate similar sentences
            s_snippet = s[:40].lower()
            if s_snippet in used_propositions:
                continue
            used_propositions.add(s_snippet)

            pg_str = f" (Page {pg})" if pg else ""
            s_clean = s.strip()
            if len(s_clean) > 300:
                s_clean = s_clean[:297] + "..."

            # Categorize principle prefix
            prefix = "Legal Principle"
            if "section 118" in s.lower() or "competent" in s.lower():
                prefix = "Witness Competency"
            elif "tutored" in s.lower() or "tutoring" in s.lower():
                prefix = "Risk of Tutoring"
            elif "corroboration" in s.lower() or "measure of caution" in s.lower():
                prefix = "Standard of Corroboration"
            elif "preliminary examination" in s.lower() or "voir dire" in s.lower():
                prefix = "Preliminary Examination"
            elif "equality" in s.lower() or "article 14" in s.lower():
                prefix = "Constitutional Equality"
            elif "article 21" in s.lower() or "speedy trial" in s.lower():
                prefix = "Right to Speedy Trial"

            response_sections.append(
                f"- **{prefix} [Evidence {idx}]{pg_str}**: {s_clean}"
            )
            count += 1
            if count >= 3:
                break

        # Fallback if no scored propositions
        if count == 0:
            for ev in parsed_evidence[:3]:
                snippet = ev["clean_text"][:200]
                pg_str = f" (Page {ev['page']})" if ev['page'] else ""
                response_sections.append(
                    f"- **Record Excerpt [Evidence {ev['idx']}]{pg_str}**: \"{snippet}...\""
                )

        # SECTION 3: Statutory Provisions Examined
        if acts or sections:
            response_sections.append("\n### Statutory Provisions Examined")
            if acts:
                response_sections.append(f"- **Enactments**: {', '.join(acts)}")
            if sections:
                response_sections.append(f"- **Sections / Articles**: {', '.join(sections)}")

        # SECTION 4: Procedural Record & Disposition
        # Check if an explicit disposition or outcome sentence exists
        disposition_found = None
        for sc, idx, pg, s in scored_sentences:
            if any(term in s.lower() for term in ["appeal is allowed", "conviction is set aside", "acquitted", "benefit of doubt", "quashed", "petition dismissed"]):
                disposition_found = (idx, s)
                break

        response_sections.append("\n### Procedural Record & Disposition")
        if disposition_found:
            idx, disp_sent = disposition_found
            response_sections.append(f"- **Order of the Court [Evidence {idx}]**: {disp_sent}")
        else:
            response_sections.append(f"- **Adjudicating Court**: {p_court}")
            if p_bench:
                response_sections.append(f"- **Bench Coram**: {p_bench}")
            if p_date:
                response_sections.append(f"- **Decision Date**: {p_date}")

        return "\n".join(response_sections)
