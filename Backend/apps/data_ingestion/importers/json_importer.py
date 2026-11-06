"""
NYAYASETU Data Ingestion — JSON Importer

Imports judicial case records from a JSON file.
JSON must be a list of objects with the same field schema as CSV.
"""
import json
import logging
from typing import Union

from apps.data_ingestion.validators import validate_case_record
from apps.data_ingestion.importers.csv_importer import import_case_from_row

logger = logging.getLogger(__name__)


def import_json(filepath: str, dry_run: bool = False) -> dict:
    """
    Import all cases from a JSON file (list of objects).

    Returns a summary dict: {created, updated, skipped, errors, total, dry_run}
    """
    summary = {"created": 0, "updated": 0, "skipped": 0, "errors": 0, "total": 0, "dry_run": dry_run}

    with open(filepath, encoding="utf-8") as fh:
        try:
            records = json.load(fh)
        except json.JSONDecodeError as exc:
            logger.error("[JSON import] Invalid JSON: %s", exc)
            summary["errors"] += 1
            return summary

    if not isinstance(records, list):
        logger.error("[JSON import] Top-level JSON must be a list of objects")
        summary["errors"] += 1
        return summary

    for row_num, record in enumerate(records, start=1):
        summary["total"] += 1

        vr = validate_case_record(record)
        if not vr.is_valid:
            for err in vr.errors:
                logger.error("[JSON import] Record %d — %s: %s", row_num, err.field, err.message)
            summary["errors"] += 1
            continue

        for warn in vr.warnings:
            logger.warning("[JSON import] Record %d — %s: %s", row_num, warn.field, warn.message)

        try:
            action, _ = import_case_from_row(record, dry_run=dry_run)
            summary[action if action != "dry_run" else "skipped"] += 1
        except Exception as exc:
            logger.exception("[JSON import] Failed to import record %d: %s", row_num, exc)
            summary["errors"] += 1

    return summary

