"""
NYAYASETU — Judicial Dataset Validation Service

Validates manifest records and downloaded PDF integrity before or after import.
"""
import csv
import logging
import os
from typing import Dict, List

from apps.data_ingestion.judicial_dataset.downloader import is_valid_pdf
from apps.data_ingestion.judicial_dataset.importer import _parse_date

logger = logging.getLogger(__name__)


def validate_manifest(manifest_filepath: str, base_dir: str) -> Dict:
    """
    Validate a judicial dataset manifest CSV.

    Returns:
        {
            "total_records": int,
            "valid_records": int,
            "invalid_records": int,
            "pdf_present_and_valid": int,
            "pdf_missing_or_corrupt": int,
            "errors": List[str],
            "warnings": List[str],
        }
    """
    if not os.path.isfile(manifest_filepath):
        raise FileNotFoundError(f"Manifest not found: {manifest_filepath}")

    with open(manifest_filepath, newline="", encoding="utf-8") as fh:
        records = list(csv.DictReader(fh))

    report = {
        "total_records": len(records),
        "valid_records": 0,
        "invalid_records": 0,
        "pdf_present_and_valid": 0,
        "pdf_missing_or_corrupt": 0,
        "errors": [],
        "warnings": [],
    }

    required_columns = {"case_id", "title", "source_url", "local_pdf_path"}
    if records:
        missing_cols = required_columns - set(records[0].keys())
        if missing_cols:
            report["errors"].append(f"Manifest missing required columns: {missing_cols}")
            report["invalid_records"] = len(records)
            return report

    for idx, row in enumerate(records, start=1):
        cid = (row.get("case_id") or "").strip()
        title = (row.get("title") or "").strip()
        local_rel = (row.get("local_pdf_path") or "").strip()
        date_str = (row.get("decision_date") or "").strip()

        row_errors = []
        if not cid:
            row_errors.append(f"Row {idx}: missing case_id")
        if not title:
            row_errors.append(f"Row {idx}: missing title")

        if date_str and not _parse_date(date_str):
            report["warnings"].append(f"Row {idx} ({cid}): unrecognized date format '{date_str}'")

        if local_rel:
            local_abs = os.path.join(base_dir, local_rel)
            if is_valid_pdf(local_abs):
                report["pdf_present_and_valid"] += 1
                row["validation_status"] = "VALID"
            else:
                report["pdf_missing_or_corrupt"] += 1
                row["validation_status"] = "PDF_MISSING"
        else:
            report["pdf_missing_or_corrupt"] += 1

        if row_errors:
            report["invalid_records"] += 1
            report["errors"].extend(row_errors)
        else:
            report["valid_records"] += 1

    return report

