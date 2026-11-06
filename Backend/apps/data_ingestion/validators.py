"""
NYAYASETU Data Ingestion — Validators

Validates raw judicial records before database insertion.
Does NOT modify data; returns structured ValidationResult.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# CNR pattern: 4-letter state code + 2-digit court code + 10 alphanumeric
# e.g. DLHC010012342023 (16 chars). We accept flexible variants too.
# ──────────────────────────────────────────────────────────────────────────────
CNR_PATTERN = re.compile(r'^[A-Z]{4}\d{2}\d{10}$')   # strict 16-char
CASE_NUMBER_PATTERN = re.compile(r'\S')               # at least one non-space


@dataclass
class FieldError:
    field: str
    message: str


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def add_error(self, field_name: str, message: str):
        self.errors.append(FieldError(field=field_name, message=message))
        self.is_valid = False

    def add_warning(self, field_name: str, message: str):
        self.warnings.append(FieldError(field=field_name, message=message))


def validate_date(value: Optional[str], field_name: str, result: ValidationResult) -> Optional[date]:
    """Parse a date string; add an error to result on failure."""
    if not value:
        return None
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            from datetime import datetime
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    result.add_warning(field_name, f"Unrecognised date format '{value}'; stored as None")
    return None


def validate_case_record(record: dict) -> ValidationResult:
    """
    Validate a single case record dict (CSV row or JSON object).
    Returns a ValidationResult with errors/warnings.
    """
    result = ValidationResult()

    # Required: case_number
    case_number = str(record.get("case_number", "")).strip()
    if not case_number:
        result.add_error("case_number", "case_number is required")
    elif not CASE_NUMBER_PATTERN.search(case_number):
        result.add_error("case_number", "case_number must contain at least one non-space character")

    # Required: case_title
    case_title = str(record.get("case_title", "")).strip()
    if not case_title:
        result.add_error("case_title", "case_title is required")
    elif len(case_title) > 500:
        result.add_warning("case_title", f"case_title truncated from {len(case_title)} to 500 chars")

    # Required: court_name
    court_name = str(record.get("court_name", "")).strip()
    if not court_name:
        result.add_error("court_name", "court_name is required (used to look-up or create Court)")

    # Optional: cnr_number format check
    cnr = str(record.get("cnr_number", "")).strip()
    if cnr and not CNR_PATTERN.match(cnr):
        result.add_warning("cnr_number", f"cnr_number '{cnr}' does not match expected 16-char CNR format; accepted anyway")

    # Optional dates
    validate_date(record.get("filing_date"), "filing_date", result)
    validate_date(record.get("decision_date"), "decision_date", result)

    # Optional: status
    valid_statuses = {"PENDING", "DISPOSED", "WITHDRAWN", "TRANSFERRED", "OTHER", "UNKNOWN"}
    status = str(record.get("status", "UNKNOWN")).strip().upper()
    if status and status not in valid_statuses:
        result.add_warning("status", f"Unknown status '{status}'; defaulting to UNKNOWN")

    return result


def validate_csv_row(row: dict, row_num: int) -> ValidationResult:
    """Wrapper that adds row context to the validation result."""
    result = validate_case_record(row)
    if not result.is_valid:
        for err in result.errors:
            err.message = f"Row {row_num}: {err.message}"
    return result

