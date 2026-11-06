"""
NYAYASETU — Judicial Dataset PDF Downloader

Downloads selected judgments PDFs from the public AWS S3 bucket.
Implements:
  - Resume & skip already downloaded valid PDFs
  - Verification of HTTP response and PDF magic bytes (%PDF-)
  - Retry logic with conservative, non-aggressive access
  - Status updates in the manifest CSV
"""
import csv
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

USER_AGENT = "NyayaSetu-Dataset-Pipeline/1.0 (B.Tech Mega Project; Academic Research)"


def is_valid_pdf(filepath: str) -> bool:
    """Verify that file exists, is non-empty, and begins with PDF header bytes."""
    if not os.path.isfile(filepath):
        return False
    if os.path.getsize(filepath) < 500:  # Valid PDFs are at least several hundred bytes
        return False
    try:
        with open(filepath, "rb") as fh:
            header = fh.read(5)
            return header.startswith(b"%PDF-")
    except Exception:
        return False


def download_single_pdf(
    source_url: str,
    destination_path: str,
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
) -> bool:
    """
    Download a single PDF from public HTTPS URL with validation and retries.
    """
    if is_valid_pdf(destination_path):
        logger.debug("PDF already exists and is valid: %s", destination_path)
        return True

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    temp_path = destination_path + ".tmp"

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(source_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    logger.warning("Attempt %d: HTTP %d for %s", attempt, resp.status, source_url)
                    continue
                content = resp.read()

            if not content.startswith(b"%PDF-"):
                logger.warning("Attempt %d: Downloaded content does not start with %%PDF- from %s", attempt, source_url)
                continue

            with open(temp_path, "wb") as fh:
                fh.write(content)

            # Atomic rename
            if os.path.isfile(destination_path):
                os.remove(destination_path)
            os.rename(temp_path, destination_path)
            return True

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, max_retries, source_url, exc)
            if os.path.isfile(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            if attempt < max_retries:
                time.sleep(retry_delay_seconds * attempt)

    return False


def download_manifest_pdfs(
    manifest_filepath: str,
    base_dir: str,
    limit: Optional[int] = None,
    delay_between_downloads: float = 0.2,
) -> Dict[str, int]:
    """
    Download PDFs listed in a manifest CSV file.

    Args:
        manifest_filepath: Path to the manifest CSV.
        base_dir: Project root or Backend directory to resolve relative paths.
        limit: Optional cap on number of PDFs to download (useful for 5-10 case test run).
        delay_between_downloads: Small pause to maintain respectful access to public S3.

    Returns:
        Summary dict: {"total": int, "downloaded": int, "already_existed": int, "failed": int}
    """
    if not os.path.isfile(manifest_filepath):
        raise FileNotFoundError(f"Manifest not found: {manifest_filepath}")

    with open(manifest_filepath, newline="", encoding="utf-8") as fh:
        records = list(csv.DictReader(fh))

    if limit is not None:
        target_records = records[:limit]
    else:
        target_records = records

    summary = {"total": len(target_records), "downloaded": 0, "already_existed": 0, "failed": 0}

    for idx, row in enumerate(target_records, start=1):
        source_url = row.get("source_url")
        local_rel = row.get("local_pdf_path")
        if not source_url or not local_rel:
            summary["failed"] += 1
            row["download_status"] = "FAILED"
            continue

        local_abs = os.path.join(base_dir, local_rel)

        if is_valid_pdf(local_abs):
            summary["already_existed"] += 1
            row["download_status"] = "DOWNLOADED"
            continue

        logger.info("[%d/%d] Downloading: %s -> %s", idx, len(target_records), source_url, local_rel)
        success = download_single_pdf(source_url, local_abs)

        if success:
            summary["downloaded"] += 1
            row["download_status"] = "DOWNLOADED"
        else:
            summary["failed"] += 1
            row["download_status"] = "FAILED"

        if delay_between_downloads > 0:
            time.sleep(delay_between_downloads)

    # Save updated manifest back
    fieldnames = list(records[0].keys())
    with open(manifest_filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    logger.info("Download complete. Summary: %s", summary)
    return summary

