"""
NYAYASETU — Judicial Dataset Discovery Service

Selects a reproducible, controlled subset of judgments from the public
Indian Supreme Court Judgments Open Dataset (AWS Open Data Registry).
Uses public HTTPS without requiring AWS credentials or paid APIs.
"""
import csv
import datetime
import io
import logging
import os
import random
import urllib.request
from typing import List, Optional

import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

AWS_S3_BASE_URL = "https://indian-supreme-court-judgments.s3.amazonaws.com"
DATASET_NAME = "Indian Supreme Court Judgments Open Dataset"
DATASET_LICENSE = "CC BY 4.0"

DEFAULT_SAMPLE_YEARS = [
    1950, 1954, 1960, 1965, 1970, 1975, 1980, 1985, 
    1990, 1995, 2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024
]

USER_AGENT = "NyayaSetu-Dataset-Pipeline/1.0 (B.Tech Mega Project; Academic Research)"


def fetch_year_metadata(year: int, cache_dir: Optional[str] = None) -> List[dict]:
    """
    Fetch and parse the Parquet metadata for a specific year from public S3.
    Caches locally to avoid redundant network requests.
    """
    parquet_url = f"{AWS_S3_BASE_URL}/metadata/parquet/year={year}/metadata.parquet"
    cache_path = os.path.join(cache_dir, f"year_{year}.parquet") if cache_dir else None

    if cache_path and os.path.isfile(cache_path) and os.path.getsize(cache_path) > 0:
        logger.info("Reading cached metadata for year %d from %s", year, cache_path)
        with open(cache_path, "rb") as fh:
            data = fh.read()
    else:
        logger.info("Downloading public metadata for year %d from %s...", year, parquet_url)
        req = urllib.request.Request(parquet_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        except Exception as exc:
            logger.warning("Could not download metadata for year %d: %s", year, exc)
            return []

        if cache_path:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "wb") as fh:
                fh.write(data)

    try:
        table = pq.read_table(io.BytesIO(data))
        raw_dict = table.to_pydict()
        num_rows = len(table)
        records = []
        for i in range(num_rows):
            rec = {col: raw_dict[col][i] for col in table.schema.names}
            records.append(rec)
        return records
    except Exception as exc:
        logger.error("Failed to parse Parquet for year %d: %s", year, exc)
        return []


def discover_supreme_court_subset(
    target_count: int = 100,
    years: Optional[List[int]] = None,
    cache_dir: Optional[str] = None,
    random_seed: int = 42,
) -> List[dict]:
    """
    Discover and select a balanced, multi-year, reproducible subset of English Supreme Court judgments.

    Returns:
        List of manifest dictionaries ready for CSV writing.
    """
    years = years or DEFAULT_SAMPLE_YEARS
    random.seed(random_seed)

    # Calculate quota per year to ensure historical diversity
    quota_per_year = max(1, (target_count + len(years) - 1) // len(years))
    selected_manifest_records: List[dict] = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for year in years:
        if len(selected_manifest_records) >= target_count:
            break

        records = fetch_year_metadata(year, cache_dir=cache_dir)
        if not records:
            continue

        # Filter: English available, valid title, valid path/case_id
        valid_candidates = []
        for r in records:
            title = (r.get("title") or "").strip()
            path = (r.get("path") or "").strip()
            case_id = (r.get("case_id") or "").strip()
            langs = (r.get("available_languages") or "").upper()

            # Must have non-empty title and path
            if not title or not path:
                continue
            # Must support English
            if langs and "ENG" not in langs and "EN" not in langs:
                continue

            valid_candidates.append(r)

        # Deterministic sorting before sampling
        valid_candidates.sort(key=lambda x: str(x.get("path", "")))

        # Take up to quota
        year_sample = valid_candidates[:quota_per_year]
        for item in year_sample:
            path = item.get("path", "").strip()
            yr = str(item.get("year") or year).strip()
            pdf_s3_key = f"data/pdf/year={yr}/english/{path}_EN.pdf"
            source_url = f"{AWS_S3_BASE_URL}/{pdf_s3_key}"
            local_pdf_rel = f"data/judicial/raw/pdfs/{yr}/{path}_EN.pdf"

            manifest_entry = {
                "case_id": item.get("case_id") or item.get("nc_display") or f"{yr}_SC_{path}",
                "title": (item.get("title") or "").strip(),
                "petitioner": (item.get("petitioner") or "").strip(),
                "respondent": (item.get("respondent") or "").strip(),
                "judge": (item.get("judge") or "").strip(),
                "citation": (item.get("citation") or "").strip(),
                "cnr": (item.get("cnr") or "").strip(),
                "decision_date": (item.get("decision_date") or "").strip(),
                "disposal_nature": (item.get("disposal_nature") or "").strip(),
                "court": "Supreme Court of India",
                "available_languages": (item.get("available_languages") or "ENG").strip(),
                "source_path": pdf_s3_key,
                "source_url": source_url,
                "dataset_name": DATASET_NAME,
                "dataset_license": DATASET_LICENSE,
                "retrieved_at": now_iso,
                "local_pdf_path": local_pdf_rel,
                "download_status": "PENDING",
                "validation_status": "PENDING",
            }
            selected_manifest_records.append(manifest_entry)
            if len(selected_manifest_records) >= target_count:
                break

    logger.info("Selected %d judgments across %d years.", len(selected_manifest_records), len(years))
    return selected_manifest_records


def write_manifest_csv(records: List[dict], output_filepath: str):
    """Save selected records into the manifest CSV file."""
    if not records:
        logger.warning("No records to write to manifest.")
        return

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    fieldnames = list(records[0].keys())

    with open(output_filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    logger.info("Saved manifest with %d entries to %s", len(records), output_filepath)
