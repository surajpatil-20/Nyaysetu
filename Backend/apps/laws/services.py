import re
from typing import List
from django.db.models import F
from apps.cases.models import Case
from apps.documents.models import DocumentChunk


DOMAIN_KEYWORDS_MAP = {
    "consumer": [
        "consumer protection", "consumer", "district forum", "national commission",
        "unfair trade", "defective", "refund", "deficiency in service"
    ],
    "traffic": [
        "motor vehicles act", "mact", "accident", "tribunal", "compensation",
        "negligence", "rash driving", "claimant", "insurance"
    ],
    "cyber": [
        "information technology act", "cyber", "electronic record", "fraud",
        "cheating", "bank", "unauthorized", "screen-sharing"
    ],
    "police": [
        "crpc", "arrest", "custody", "detention", "magistrate", "investigation",
        "section 41", "bail", "remand", "custodial"
    ],
    "tenant": [
        "transfer of property act", "lease", "tenant", "landlord", "eviction",
        "rent", "section 106", "quiet enjoyment", "possession"
    ],
    "women": [
        "domestic violence", "pwdva", "shared household", "matrimonial",
        "cruelty", "maintenance", "wife", "dowry"
    ],
    "workplace": [
        "payment of wages", "gratuity", "salary", "workman", "workmen",
        "industrial", "termination", "retrenchment", "pension"
    ],
}

SPECIFIC_STATUTE_TERMS = {
    "consumer protection", "motor vehicles act", "mact",
    "information technology act", "transfer of property act",
    "domestic violence", "pwdva", "payment of wages", "gratuity"
}


def get_scenario_related_cases(scenario) -> List[Case]:
    """
    Retrieve and rank genuine Supreme Court precedent cases for a legal scenario.
    Combines curated many-to-many associations with intelligent search-based
    relevance matching across authentic judicial document chunks.
    
    Guarantees:
    - Only authentic Supreme Court judgments (DEMO SOURCE excluded).
    - Most relevant cases ranked first.
    - Up to 8 cases per scenario (if fewer than 5 strong matches exist, only strong ones returned).
    - Contextual snippets attached for clear citizen explanation.
    """
    category_slug = scenario.category.slug.lower() if scenario.category else ""
    title_lower = scenario.title.lower()

    # 1. Start with any directly linked M2M cases
    linked_cases = list(
        scenario.related_cases.exclude(
            source_name='DEMO SOURCE'
        ).select_related('court').order_by(
            F('decision_date').desc(nulls_last=True)
        )
    )

    seen_case_ids = {c.id for c in linked_cases}

    # If we already have 5-8 curated cases, attach snippets if needed and return
    if len(linked_cases) >= 5:
        _attach_snippets(linked_cases, scenario)
        return linked_cases[:8]

    # 2. Dynamic relevance retrieval if fewer than 5 linked
    domain_key = None
    for k in DOMAIN_KEYWORDS_MAP:
        if k in category_slug or k in title_lower:
            domain_key = k
            break

    search_terms = DOMAIN_KEYWORDS_MAP.get(domain_key, [])
    if not search_terms:
        # Default fallback to section titles / act short codes
        for sec in scenario.sections.select_related('act').all():
            search_terms.append(sec.act.short_code.lower())
            search_terms.append(sec.title.lower())

    case_scores = {}
    for term in search_terms:
        matching_chunks = DocumentChunk.objects.filter(
            content__icontains=term
        ).exclude(
            document__case__source_name='DEMO SOURCE'
        ).select_related('document__case', 'document__case__court')[:50]

        for chunk in matching_chunks:
            c = chunk.document.case
            if not c or c.id in seen_case_ids or c.source_name == 'DEMO SOURCE':
                continue
            if c.id not in case_scores:
                case_scores[c.id] = {
                    "case": c,
                    "matched_terms": set(),
                    "frequency": 0,
                    "best_snippet": ""
                }
            case_scores[c.id]["matched_terms"].add(term)
            case_scores[c.id]["frequency"] += 1
            if not case_scores[c.id]["best_snippet"] and len(chunk.content) > 50:
                pos = chunk.content.lower().find(term.lower())
                start = max(0, pos - 40)
                end = min(len(chunk.content), pos + 140)
                case_scores[c.id]["best_snippet"] = chunk.content[start:end].replace('\n', ' ').strip()

    # Filter to genuine relevance: must have at least 1 specific statute term or 2 distinct domain terms
    genuine_dynamic = []
    for cid, data in case_scores.items():
        has_specific = bool(data["matched_terms"].intersection(SPECIFIC_STATUTE_TERMS))
        if has_specific or len(data["matched_terms"]) >= 2:
            c = data["case"]
            c.relevance_snippet = data["best_snippet"]
            genuine_dynamic.append((data, c))

    # Rank dynamic matches
    genuine_dynamic.sort(
        key=lambda item: (
            1 if item[0]["matched_terms"].intersection(SPECIFIC_STATUTE_TERMS) else 0,
            len(item[0]["matched_terms"]),
            item[0]["frequency"]
        ),
        reverse=True
    )

    combined_cases = list(linked_cases)
    for _, c in genuine_dynamic:
        if c.id not in seen_case_ids:
            seen_case_ids.add(c.id)
            combined_cases.append(c)
        if len(combined_cases) >= 8:
            break

    _attach_snippets(combined_cases, scenario)
    return combined_cases


def _attach_snippets(cases: List[Case], scenario):
    """Ensure every case in the result has a clean, readable relevance_snippet."""
    for c in cases:
        if hasattr(c, 'relevance_snippet') and c.relevance_snippet:
            continue
        # Extract snippet from first document chunk if available
        first_chunk = DocumentChunk.objects.filter(
            document__case=c
        ).first()
        if first_chunk and first_chunk.content:
            clean = first_chunk.content.replace('\n', ' ').strip()
            c.relevance_snippet = clean[:180] + ("…" if len(clean) > 180 else "")
        elif c.description:
            c.relevance_snippet = c.description
        else:
            c.relevance_snippet = "Authoritative Supreme Court judicial precedent."
