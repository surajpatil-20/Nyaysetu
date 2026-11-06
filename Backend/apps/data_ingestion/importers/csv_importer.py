"""
NYAYASETU Data Ingestion — CSV Importer

Imports judicial case records from a CSV file.
Idempotent: matches by CNR → (case_number, court) → skips duplicates.

Expected CSV columns (all except case_number, case_title, court_name are optional):
  case_number, case_title, court_name, court_type, court_state,
  cnr_number, case_type, filing_date, decision_date, status,
  description, source_url, source_name, petitioner, respondent,
  judge_name, judge_designation
"""
import csv
import logging
from datetime import datetime
from typing import Optional

from django.db import transaction

from apps.cases.models import Case, Party, CaseParty, CaseJudge
from apps.courts.models import Court, Judge
from apps.sources.models import Source
from apps.data_ingestion.validators import validate_csv_row

logger = logging.getLogger(__name__)


def _parse_date(value: Optional[str]):
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    logger.warning("Could not parse date: %s", value)
    return None


def _get_or_create_court(court_name: str, court_type: str = "", state: str = "") -> Court:
    """Get existing court or create a new one."""
    court, created = Court.objects.get_or_create(
        court_name=court_name,
        defaults={
            "court_type": court_type or Court.CourtType.OTHER,
            "state": state or None,
        }
    )
    if created:
        logger.info("Created new Court: %s", court_name)
    return court


def _get_or_create_source(source_name: str, source_url: str = "") -> Source:
    """Get or create a Source record."""
    source, created = Source.objects.get_or_create(
        source_name=source_name,
        defaults={
            "source_url": source_url or None,
            "source_type": Source.SourceType.OTHER,
            "reliability_status": Source.ReliabilityStatus.VERIFIED_PUBLIC,
        }
    )
    return source


def _add_party(case: Case, name: str, role: str):
    """Add a party to a case if not already present."""
    if not name or not name.strip():
        return
    party, _ = Party.objects.get_or_create(name=name.strip())
    CaseParty.objects.get_or_create(
        case=case,
        party=party,
        defaults={"role": role}
    )


def _add_judge(case: Case, name: str, designation: str = "", court: Optional[Court] = None):
    """Add a judge assignment to a case if not already present."""
    if not name or not name.strip():
        return
    judge, _ = Judge.objects.get_or_create(
        name=name.strip(),
        defaults={
            "designation": designation or None,
            "current_court": court,
        }
    )
    CaseJudge.objects.get_or_create(
        case=case,
        judge=judge,
        defaults={"role": CaseJudge.JudgeRole.PRESIDING}
    )


@transaction.atomic
def import_case_from_row(row: dict, dry_run: bool = False) -> tuple:
    """
    Import a single case row.

    Returns:
        (action, case_or_None)
        action: 'created' | 'updated' | 'skipped' | 'error'
    """
    case_number = str(row.get("case_number", "")).strip()
    case_title = str(row.get("case_title", "")).strip()
    court_name = str(row.get("court_name", "")).strip()
    cnr_number = str(row.get("cnr_number", "")).strip() or None

    court_type = str(row.get("court_type", "")).strip().upper()
    court_state = str(row.get("court_state", "")).strip()
    case_type = str(row.get("case_type", "")).strip() or None
    filing_date = _parse_date(row.get("filing_date"))
    decision_date = _parse_date(row.get("decision_date"))

    raw_status = str(row.get("status", "UNKNOWN")).strip().upper()
    valid_statuses = {c.value for c in Case.CaseStatus}
    status = raw_status if raw_status in valid_statuses else "UNKNOWN"

    description = str(row.get("description", "")).strip() or None
    source_url = str(row.get("source_url", "")).strip() or None
    source_name_str = str(row.get("source_name", "")).strip()

    petitioner = str(row.get("petitioner", "")).strip()
    respondent = str(row.get("respondent", "")).strip()
    judge_name = str(row.get("judge_name", "")).strip()
    judge_designation = str(row.get("judge_designation", "")).strip()

    if dry_run:
        return ("dry_run", None)

    court = _get_or_create_court(court_name, court_type, court_state)
    source = _get_or_create_source(source_name_str, source_url) if source_name_str else None

    # Idempotency: try CNR first, then case_number+court
    case = None
    action = "created"

    if cnr_number:
        try:
            case = Case.objects.get(cnr_number=cnr_number)
            action = "updated"
        except Case.DoesNotExist:
            pass

    if case is None:
        try:
            case = Case.objects.get(case_number=case_number, court=court)
            action = "updated"
        except Case.DoesNotExist:
            pass

    if case is None:
        case = Case(case_number=case_number, court=court)

    # Apply fields
    case.case_title = case_title[:500]
    case.case_type = case_type
    case.cnr_number = cnr_number
    case.filing_date = filing_date
    case.decision_date = decision_date
    case.status = status
    case.description = description
    case.source_url = source_url
    case.source_name = source_name_str or None
    if source:
        case.source = source
    case.save()

    _add_party(case, petitioner, CaseParty.PartyRole.PETITIONER)
    _add_party(case, respondent, CaseParty.PartyRole.RESPONDENT)
    _add_judge(case, judge_name, judge_designation, court)

    return (action, case)


def import_csv(filepath: str, dry_run: bool = False) -> dict:
    """
    Import all cases from a CSV file.

    Returns a summary dict:
        {created, updated, skipped, errors, total, dry_run}
    """
    summary = {"created": 0, "updated": 0, "skipped": 0, "errors": 0, "total": 0, "dry_run": dry_run}

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row_num, row in enumerate(reader, start=2):   # row 1 is header
            summary["total"] += 1

            # Validate first
            vr = validate_csv_row(row, row_num)
            if not vr.is_valid:
                for err in vr.errors:
                    logger.error("[CSV import] Validation error — %s: %s", err.field, err.message)
                summary["errors"] += 1
                continue

            for warn in vr.warnings:
                logger.warning("[CSV import] Warning — %s: %s", warn.field, warn.message)

            try:
                action, _ = import_case_from_row(row, dry_run=dry_run)
                summary[action if action != "dry_run" else "skipped"] += 1
            except Exception as exc:
                logger.exception("[CSV import] Failed to import row %d: %s", row_num, exc)
                summary["errors"] += 1

    return summary

