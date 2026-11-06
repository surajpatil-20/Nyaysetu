"""
NYAYASETU — Judicial Dataset Importer

Imports real Supreme Court judgments and PDF documents into the existing
PostgreSQL models with provenance, idempotency, and document pipeline integration.
"""
import csv
import datetime
import logging
import os
import re
from typing import Dict, List, Optional

from django.core.files import File
from django.db import transaction

from apps.cases.models import Case, CaseJudge, CaseParty, Party
from apps.courts.models import Court, Judge
from apps.documents.models import Document
from apps.documents.services.chunking import chunk_document
from apps.documents.services.embeddings import generate_embeddings_for_document
from apps.documents.services.extraction import process_document
from apps.sources.models import Source

logger = logging.getLogger(__name__)

DATASET_NAME = "Indian Supreme Court Judgments Open Dataset"
DATASET_LICENSE = "CC BY 4.0"
AWS_S3_BASE_URL = "https://indian-supreme-court-judgments.s3.amazonaws.com"


def _parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    """Parse various date formats from the dataset (e.g., DD-MM-YYYY, YYYY-MM-DD)."""
    if not date_str:
        return None
    date_str = str(date_str).strip()
    if not date_str:
        return None
    for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d %b %Y"]:
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _get_or_create_supreme_court() -> Court:
    """Ensure a single canonical Supreme Court of India record exists."""
    court, _ = Court.objects.get_or_create(
        court_name="Supreme Court of India",
        defaults={
            "court_type": Court.CourtType.SUPREME_COURT,
            "court_code": "SCI",
            "state": "Delhi",
            "city": "New Delhi",
            "source_url": "https://www.sci.gov.in",
        }
    )
    return court


def _get_or_create_dataset_source() -> Source:
    """Ensure a canonical Source record representing the AWS Open Dataset exists."""
    source, _ = Source.objects.get_or_create(
        source_name=DATASET_NAME,
        defaults={
            "source_url": AWS_S3_BASE_URL,
            "source_type": Source.SourceType.PUBLIC_ARCHIVE,
            "reliability_status": Source.ReliabilityStatus.OFFICIAL,
            "description": f"{DATASET_NAME} (1950–2025), Registry of Open Data on AWS, License: {DATASET_LICENSE}",
        }
    )
    return source


def _clean_entity_name(name: str) -> str:
    """Normalize excess whitespace without altering judicial text."""
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def _attach_parties(case: Case, petitioner_name: str, respondent_name: str):
    """Link petitioner and respondent party entities."""
    if petitioner_name:
        p_clean = _clean_entity_name(petitioner_name)[:300]
        p_obj, _ = Party.objects.get_or_create(
            name=p_clean,
            defaults={"party_type": Party.PartyType.OTHER}
        )
        CaseParty.objects.get_or_create(
            case=case,
            party=p_obj,
            defaults={"role": CaseParty.PartyRole.PETITIONER}
        )

    if respondent_name:
        r_clean = _clean_entity_name(respondent_name)[:300]
        r_obj, _ = Party.objects.get_or_create(
            name=r_clean,
            defaults={"party_type": Party.PartyType.OTHER}
        )
        CaseParty.objects.get_or_create(
            case=case,
            party=r_obj,
            defaults={"role": CaseParty.PartyRole.RESPONDENT}
        )


def _attach_judges(case: Case, judge_raw: str, court: Court):
    """Parse and link judges named in the dataset."""
    if not judge_raw or not judge_raw.strip():
        return
    # Split by common delimiters if multiple judges listed
    raw_names = re.split(r'[,;]|\band\b', judge_raw, flags=re.IGNORECASE)
    bench_order = 1
    for raw in raw_names:
        clean = _clean_entity_name(raw)
        if not clean or len(clean) < 3:
            continue
        judge_obj, _ = Judge.objects.get_or_create(
            name=clean[:255],
            defaults={
                "current_court": court,
                "designation": "Judge, Supreme Court of India",
            }
        )
        CaseJudge.objects.get_or_create(
            case=case,
            judge=judge_obj,
            defaults={
                "role": CaseJudge.JudgeRole.PRESIDING if bench_order == 1 else CaseJudge.JudgeRole.MEMBER,
                "bench_order": bench_order,
            }
        )
        bench_order += 1


@transaction.atomic
def import_manifest_row(
    row: dict,
    base_dir: str,
    court: Court,
    source: Source,
    dry_run: bool = False,
    auto_process: bool = False,
    auto_embed: bool = False,
) -> tuple:
    """
    Import a single manifest record into PostgreSQL.

    Returns:
        (status_string, case_or_none, document_or_none)
    """
    case_id = (row.get("case_id") or "").strip()
    title = (row.get("title") or "").strip()
    cnr = (row.get("cnr") or "").strip() or None
    decision_date = _parse_date(row.get("decision_date"))
    citation = (row.get("citation") or "").strip()
    disposal = (row.get("disposal_nature") or "").strip()
    source_url = (row.get("source_url") or "").strip() or None
    local_rel = (row.get("local_pdf_path") or "").strip()

    if not case_id or not title:
        return ("invalid_metadata", None, None)

    local_abs = os.path.join(base_dir, local_rel) if local_rel else None
    has_pdf = local_abs and os.path.isfile(local_abs) and os.path.getsize(local_abs) > 500

    if dry_run:
        # Check if it would be create or update
        exists = False
        if cnr and Case.objects.filter(cnr_number=cnr).exists():
            exists = True
        elif Case.objects.filter(case_number=case_id, court=court).exists():
            exists = True
        action = "would_update" if exists else "would_create"
        return (action, None, None)

    # Idempotent match: CNR first, then (case_number, court)
    case = None
    created = False

    if cnr:
        try:
            case = Case.objects.get(cnr_number=cnr)
        except Case.DoesNotExist:
            pass

    if case is None:
        try:
            case = Case.objects.get(case_number=case_id, court=court)
        except Case.DoesNotExist:
            pass

    if case is None:
        case = Case(case_number=case_id, court=court)
        created = True

    # Map fields
    case.case_title = title[:500]
    case.case_type = "Supreme Court Judgment"
    case.cnr_number = cnr
    case.decision_date = decision_date
    case.status = Case.CaseStatus.DISPOSED
    case.source = source
    case.source_name = DATASET_NAME
    case.source_url = source_url
    desc_parts = []
    if citation:
        desc_parts.append(f"Citation: {citation}")
    if disposal:
        desc_parts.append(f"Disposal: {disposal}")
    case.description = " | ".join(desc_parts) if desc_parts else None
    case.save()

    # Link parties and judges
    _attach_parties(case, row.get("petitioner", ""), row.get("respondent", ""))
    _attach_judges(case, row.get("judge", ""), court)

    # Link Document
    doc = None
    if has_pdf:
        doc_title = f"Judgment in {case_id} — {title[:150]}"
        doc, _ = Document.objects.get_or_create(
            case=case,
            document_type=Document.DocumentType.JUDGMENT,
            defaults={
                "title": doc_title,
                "document_date": decision_date,
                "language": "en",
                "source_name": DATASET_NAME,
                "source_url": source_url,
            }
        )
        # Attach PDF file if not already attached
        if not doc.file or not os.path.isfile(doc.file.path):
            with open(local_abs, "rb") as fh:
                doc.file.save(os.path.basename(local_abs), File(fh), save=True)

        # Trigger document processing pipeline if requested
        if auto_process and doc.extraction_status != Document.ExtractionStatus.COMPLETED:
            if process_document(doc):
                chunk_document(doc)
                if auto_embed:
                    generate_embeddings_for_document(doc)

    action = "created" if created else "updated"
    return (action, case, doc)


def import_judicial_dataset(
    manifest_filepath: str,
    base_dir: str,
    limit: Optional[int] = None,
    dry_run: bool = False,
    auto_process: bool = False,
    auto_embed: bool = False,
) -> Dict[str, int]:
    """
    Import judicial dataset entries from a manifest CSV into PostgreSQL.
    """
    if not os.path.isfile(manifest_filepath):
        raise FileNotFoundError(f"Manifest not found: {manifest_filepath}")

    with open(manifest_filepath, newline="", encoding="utf-8") as fh:
        records = list(csv.DictReader(fh))

    if limit is not None:
        records = records[:limit]

    summary = {
        "total": len(records),
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "invalid": 0,
        "documents_linked": 0,
        "dry_run": dry_run,
    }

    court = _get_or_create_supreme_court()
    source = _get_or_create_dataset_source()

    for idx, row in enumerate(records, start=1):
        try:
            action, case, doc = import_manifest_row(
                row=row,
                base_dir=base_dir,
                court=court,
                source=source,
                dry_run=dry_run,
                auto_process=auto_process,
                auto_embed=auto_embed,
            )
            if action in ("created", "would_create"):
                summary["created"] += 1
            elif action in ("updated", "would_update"):
                summary["updated"] += 1
            elif action == "invalid_metadata":
                summary["invalid"] += 1
            else:
                summary["skipped"] += 1

            if doc:
                summary["documents_linked"] += 1

        except Exception as exc:
            logger.exception("Failed to import record %d (%s): %s", idx, row.get("case_id"), exc)
            summary["invalid"] += 1

    logger.info("Import complete. Summary: %s", summary)
    return summary
