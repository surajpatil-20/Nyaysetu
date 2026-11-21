"""
NYAYASETU Case Identification Service

Identifies which Supreme Court case a user is referring to among authentic cases.
Supports:
  1. Conversational continuity ("what happened in this case?", "who were the judges?")
  2. Official INSC citations and docket numbers (e.g. "2023 INSC 599", "INSC 604")
  3. Adversarial party captions ("Pradeep v State of Haryana", "S. Narahari vs S.R. Kumar")
  4. Distinctive party names ("Munshi Ram", "Santhosh Maize", "Parameshwarappa")
  5. Judge and Coram references ("Abhay S. Oka", "Krishna Murari")
  6. Disambiguation for ambiguous queries (e.g. "Union of India", "State of Haryana")
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from django.db.models import Q
from apps.cases.models import Case, Party, CaseParty, CaseJudge

logger = logging.getLogger(__name__)

# Common generic entities that appear across dozens of Indian Supreme Court cases
GENERIC_PARTIES = {
    "union of india", "uoi", "state of haryana", "state of maharashtra",
    "state of uttar pradesh", "state of u.p.", "state of up", "state of madhya pradesh",
    "state of punjab", "state of west bengal", "state of tamil nadu",
    "state of andhra pradesh", "state of orissa", "state of bihar",
    "state of karnataka", "state of gujarat", "state of kerala", "state of rajasthan",
    "commissioner of income tax", "commissioner of income-tax", "income tax officer",
    "union", "state", "the state", "govt", "government", "municipal corporation",
    "collector", "district magistrate"
}

QUESTION_PREFIX_REGEX = re.compile(
    r'^(?:can\s+you\s+)?(?:tell\s+me\s+about|what\s+happened\s+in|what\s+happened\s+with|'
    r'who\s+were\s+the\s+judges\s+(?:in|of)|who\s+was\s+the\s+judge\s+(?:in|of)|'
    r'what\s+was\s+the\s+(?:decision|holding|ruling|ratio|outcome|order)\s+in|'
    r'what\s+did\s+the\s+(?:court|supreme\s+court)\s+(?:hold|decide|rule)\s+in|'
    r'explain\s+the\s+case\s+of|explain|summary\s+of|details\s+of|case\s+of|'
    r'inquiry\s+about|in\s+the\s+matter\s+of|about|information\s+on|facts\s+of)\s+',
    re.IGNORECASE
)

CONTEXTUAL_QUERY_PATTERNS = [
    re.compile(r'\b(?:this|the)\s+case\b', re.IGNORECASE),
    re.compile(r'\bin\s+this\s+matter\b', re.IGNORECASE),
    re.compile(r'\bwhat\s+happened\b', re.IGNORECASE),
    re.compile(r'\bwho\s+were\s+the\s+judges\b', re.IGNORECASE),
    re.compile(r'\bwho\s+was\s+the\s+judge\b', re.IGNORECASE),
    re.compile(r'\bwhat\s+was\s+the\s+(?:decision|holding|ratio|outcome|order)\b', re.IGNORECASE),
    re.compile(r'\bwho\s+was\s+the\s+(?:petitioner|appellant|respondent)\b', re.IGNORECASE),
    re.compile(r'\bsummarize\s+(?:this|the)\s+matter\b', re.IGNORECASE),
]


@dataclass
class CaseResolutionResult:
    status: str  # "IDENTIFIED", "AMBIGUOUS", "NONE"
    identified_case: Optional[Case] = None
    candidate_cases: list[Case] = field(default_factory=list)
    match_reason: str = ""
    clarification_message: str = ""


def _clean_party_text(text: str) -> str:
    """Normalize party token for fuzzy/substring search."""
    cleaned = re.sub(r'\b(?:and\s+others|and\s+ors|ors\.?|anr\.?|etc\.?|the|ltd\.?|pvt\.?)\b', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()


def resolve_case_reference(query: str, context_case_id: Optional[int] = None) -> CaseResolutionResult:
    """
    Analyze the user's query and resolve whether it targets a specific Supreme Court case.

    Returns CaseResolutionResult with status in {"IDENTIFIED", "AMBIGUOUS", "NONE"}.
    """
    if not query or not query.strip():
        return CaseResolutionResult(status="NONE")

    query_clean = query.strip()
    authentic_cases = Case.objects.exclude(source_name="DEMO SOURCE")

    # -------------------------------------------------------------
    # 1. Contextual Continuity Check
    # If the user asks "what happened in this case?", "who were the judges?", etc.
    # and context_case_id is provided, check if query explicitly names another case.
    # -------------------------------------------------------------
    has_context_phrase = any(p.search(query_clean) for p in CONTEXTUAL_QUERY_PATTERNS)
    has_explicit_insc = bool(re.search(r'\bINSC\s+\d+\b', query_clean, re.IGNORECASE))
    has_adversarial = bool(re.search(r'\b(?:versus|vs\.?|v\.?)\b', query_clean, re.IGNORECASE))

    if context_case_id and has_context_phrase and not has_explicit_insc and not has_explicit_adversarial(query_clean):
        try:
            active_case = authentic_cases.select_related("court").prefetch_related("case_judges__judge").get(pk=context_case_id)
            return CaseResolutionResult(
                status="IDENTIFIED",
                identified_case=active_case,
                match_reason=f"Contextual reference to active precedent: {active_case.case_title}",
            )
        except Case.DoesNotExist:
            logger.debug("Provided context_case_id=%s not found among authentic cases", context_case_id)

    # -------------------------------------------------------------
    # 2. INSC Citation / Case Number Extraction
    # Pattern: [YYYY] INSC [N] or INSC [N]
    # -------------------------------------------------------------
    insc_match = re.search(r'\b(?:(19\d{2}|20\d{2})\s+)?INSC\s+(\d+)\b', query_clean, re.IGNORECASE)
    if insc_match:
        year_str = insc_match.group(1)
        num_str = insc_match.group(2)
        qs = authentic_cases
        if year_str:
            qs = qs.filter(case_number__icontains=f"{year_str} INSC {num_str}")
        else:
            qs = qs.filter(case_number__icontains=f"INSC {num_str}")

        candidates = list(qs[:5])
        if len(candidates) == 1:
            return CaseResolutionResult(
                status="IDENTIFIED",
                identified_case=candidates[0],
                match_reason=f"Matched official citation: {candidates[0].case_number}",
            )
        elif len(candidates) > 1:
            return _build_ambiguous_result(
                query_clean,
                candidates,
                reason=f"Multiple Supreme Court decisions match INSC {num_str}"
            )

    # -------------------------------------------------------------
    # 3. Adversarial Party Notation ("Party A v. Party B")
    # -------------------------------------------------------------
    stripped_query = QUESTION_PREFIX_REGEX.sub('', query_clean).strip(' ?.!')
    v_match = re.search(
        r'([A-Za-z0-9\.\s&\'-]+?)\s+(?:versus|vs\.?|v\.?)\s+([A-Za-z0-9\.\s&\'-]+)',
        stripped_query,
        re.IGNORECASE
    )

    if v_match:
        p1_raw = v_match.group(1).strip()
        p2_raw = v_match.group(2).strip()
        p1 = _clean_party_text(p1_raw)
        p2 = _clean_party_text(p2_raw)

        if len(p1) >= 3 and len(p2) >= 3:
            # Query candidate cases where both parties or terms appear in case_title or party records
            qs = authentic_cases.filter(
                (Q(case_title__icontains=p1) | Q(case_parties__party__name__icontains=p1)) &
                (Q(case_title__icontains=p2) | Q(case_parties__party__name__icontains=p2))
            ).distinct()

            candidates = list(qs[:5])
            if len(candidates) == 1:
                return CaseResolutionResult(
                    status="IDENTIFIED",
                    identified_case=candidates[0],
                    match_reason=f"Matched case caption: {p1_raw} v. {p2_raw}",
                )
            elif len(candidates) > 1:
                return _build_ambiguous_result(
                    query_clean,
                    candidates,
                    reason=f"Multiple cases match caption '{p1_raw} v. {p2_raw}'"
                )

    # -------------------------------------------------------------
    # 4. Distinctive Party Name or Case Title Substring Search
    # -------------------------------------------------------------
    # Extract candidate query phrases (excluding generic filler words)
    candidate_tokens = [
        t for t in re.split(r'[,;.!?\n]+', stripped_query)
        if len(t.strip()) >= 3
    ]
    if not candidate_tokens:
        candidate_tokens = [stripped_query]

    scored_cases: dict[int, tuple[float, Case, str]] = {}

    for phrase in candidate_tokens:
        phrase_clean = _clean_party_text(phrase)
        if len(phrase_clean) < 3:
            continue

        phrase_lower = phrase_clean.lower()
        is_generic = phrase_lower in GENERIC_PARTIES

        # Exact or partial title / party match
        matching_qs = authentic_cases.filter(
            Q(case_title__icontains=phrase_clean) |
            Q(case_parties__party__name__icontains=phrase_clean)
        ).distinct()

        match_count = matching_qs.count()
        if match_count == 0:
            continue

        for case in matching_qs[:8]:
            cid = case.pk
            existing_score, _, _ = scored_cases.get(cid, (0.0, case, ""))

            # Score based on distinctiveness
            if is_generic:
                add_score = 15.0
                reason = f"Contains generic party '{phrase_clean}'"
            elif match_count == 1:
                add_score = 60.0
                reason = f"Uniquely matched distinctive party '{phrase_clean}'"
            elif match_count <= 3:
                add_score = 35.0
                reason = f"Matched party '{phrase_clean}' across {match_count} cases"
            else:
                add_score = 20.0
                reason = f"Matched party '{phrase_clean}'"

            # Boost if query contains other words from case title or description
            title_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', case.case_title.lower()))
            q_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', query_clean.lower())) - {"what", "held", "case", "state", "the"}
            overlap = len(title_words.intersection(q_words))
            add_score += overlap * 10.0

            scored_cases[cid] = (existing_score + add_score, case, reason)

    # -------------------------------------------------------------
    # 5. Judge / Coram Search
    # e.g. "Abhay S. Oka", "Krishna Murari", "Rajesh Bindal"
    # -------------------------------------------------------------
    judge_matches = CaseJudge.objects.filter(
        case__in=authentic_cases,
        judge__name__icontains=stripped_query
    ).select_related("case", "judge")[:5]

    for cj in judge_matches:
        cid = cj.case_id
        existing_score, _, _ = scored_cases.get(cid, (0.0, cj.case, ""))
        scored_cases[cid] = (
            existing_score + 40.0,
            cj.case,
            f"Adjudicated by Hon'ble Judge {cj.judge.name}"
        )

    # -------------------------------------------------------------
    # 6. Evaluate Scored Candidates & Clarification Logic
    # -------------------------------------------------------------
    if not scored_cases:
        return CaseResolutionResult(status="NONE")

    # Sort descending by score
    sorted_candidates = sorted(scored_cases.values(), key=lambda x: x[0], reverse=True)
    top_score, top_case, top_reason = sorted_candidates[0]

    # Check for ambiguity among top candidates
    plausible_candidates = [c for s, c, r in sorted_candidates if s >= 20.0]

    # If the top score is sufficiently confident and clearly beats 2nd candidate
    if top_score >= 50.0:
        if len(sorted_candidates) == 1:
            return CaseResolutionResult(
                status="IDENTIFIED",
                identified_case=top_case,
                match_reason=top_reason,
            )
        second_score = sorted_candidates[1][0]
        if top_score - second_score >= 20.0:
            return CaseResolutionResult(
                status="IDENTIFIED",
                identified_case=top_case,
                match_reason=top_reason,
            )

    # If multiple candidates are plausible with close scores -> Clarify!
    if len(plausible_candidates) >= 2:
        top_candidates = [c for _, c, _ in sorted_candidates[:4]]
        return _build_ambiguous_result(
            query_clean,
            top_candidates,
            reason="Multiple Supreme Court cases in the NYAYASETU repository match your inquiry"
        )
    elif top_score >= 40.0:
        return CaseResolutionResult(
            status="IDENTIFIED",
            identified_case=top_case,
            match_reason=top_reason,
        )

    # No confident case match -> fallback to general RAG
    return CaseResolutionResult(status="NONE")


def has_explicit_adversarial(query: str) -> bool:
    """Check if query contains 'versus', 'vs', or 'v.' adversarial token."""
    return bool(re.search(r'\b(?:versus|vs\.?|v\.?)\b', query, re.IGNORECASE))


def _build_ambiguous_result(query: str, candidates: list[Case], reason: str) -> CaseResolutionResult:
    """Format an informative clarification message listing plausible candidate cases."""
    lines = [
        f"{reason}. Please clarify which specific precedent you would like to examine:\n"
    ]
    for idx, c in enumerate(candidates, start=1):
        c_date = f", decided on {c.decision_date}" if c.decision_date else ""
        c_bench = ""
        judges = [cj.judge.name for cj in c.case_judges.all()]
        if judges:
            c_bench = f" (Bench: {', '.join(judges)})"
        lines.append(f"{idx}. **{c.case_title}** [{c.case_number}{c_date}]{c_bench}")

    lines.append("\nYou can select one of the suggested precedents above or specify the complete case title or citation.")

    return CaseResolutionResult(
        status="AMBIGUOUS",
        candidate_cases=candidates,
        match_reason=reason,
        clarification_message="\n".join(lines),
    )
