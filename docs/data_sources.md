# NYAYASETU — Data Sources & Attribution Documentation

This document describes the external data sources, licensing, provenance, and tracing mechanisms utilized by **NYAYASETU — An AI-Assisted, Evidence-Oriented Judicial Information Platform**.

---

## 1. Primary Dataset Information

| Attribute | Specification |
|---|---|
| **Dataset Name** | Indian Supreme Court Judgments Open Dataset |
| **Provider / Host** | Registry of Open Data on AWS |
| **Original Authority** | Supreme Court of India (Public Records) |
| **Coverage** | 1950 – 2025 (Complete Supreme Court English Corpus) |
| **License** | Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)) |
| **Access Model** | Free, Public, Open Access (No AWS account or API key required) |
| **Access URLs** | S3 URI: `s3://indian-supreme-court-judgments/`<br>Public HTTPS: `https://indian-supreme-court-judgments.s3.amazonaws.com/` |
| **Initial Retrieval Date** | November 6, 2026 |

---

## 2. Recommended Academic & Open Data Citation

When publishing research, reports, or data derived from this dataset, cite:

> **Indian Supreme Court Judgments Open Dataset (1950–2025)**.  
> Hosted on the Registry of Open Data on AWS. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).  
> Available at: `https://indian-supreme-court-judgments.s3.amazonaws.com/`

---

## 3. Strict Compliance & Free-Tier Rules

NYAYASETU operates strictly within ethical, open-access, and legal boundaries:

1. **No Paid Dependencies**: NYAYASETU does NOT use Indian Kanoon paid APIs, commercial legal databases (SCC Online, Manupatra, LexisNexis), paid OCR services, or commercial embedding APIs.
2. **Controlled Ingestion**: To ensure efficient development and respect for public infrastructure, NYAYASETU does not scrape aggressively or download the entire 35,000+ corpus at once. A balanced, reproducible development dataset of ~100 judgments is sampled across decades (1950–2024).
3. **No Anti-Bot or CAPTCHA Bypasses**: Data is retrieved exclusively from documented, sanctioned, open-access S3 endpoints.

---

## 4. Local Storage & Artifact Locations

In accordance with project repository hygiene, large raw PDFs are excluded from version control (`.gitignore`), while reproducible manifests remain version-tracked:

```text
Backend/data/judicial/
├── manifests/
│   └── supreme_court_phase1.csv   # Version-controlled reproducible manifest (100 cases)
├── raw/
│   ├── metadata/                  # Cached Parquet metadata files by year
│   │   ├── year_1950.parquet
│   │   └── ...
│   └── pdfs/                      # Downloaded original judgment PDFs (git-ignored)
│       ├── 1950/
│       │   └── 1950_1_806_821_EN.pdf
│       └── ...
└── processed/                     # Text extractions and intermediate pipelines
```

---

## 5. End-to-End Source Provenance & User Tracing

Every record imported into NYAYASETU maintains complete, verifiable provenance so citizens and researchers can trace AI-generated answers back to the official primary record:

1. **Database Source Provenance**:
   - `Case.source_name`: `"Indian Supreme Court Judgments Open Dataset"`
   - `Case.source_url`: Direct public link to the judgment PDF on AWS Open Data
   - `Case.cnr_number`: Official Case National Identifier (eCourts CNR)
   - `Case.case_number`: Neutral citation / docket identifier (e.g., `1950 INSC 25`)
   - `Case.description`: Official SCR citation (e.g., `[1950] 1 S.C.R. 806`)
2. **Document-Level Grounding**:
   - `Document.file`: Stored original PDF
   - `Document.source_url`: Verifiable remote URL
   - `DocumentChunk.page_number`: Exact PDF page where each excerpt originates
3. **RAG Citations**:
   - The AI Assistant formats each evidence item with `[Evidence N]`, specifying the case caption, court, judgment date, page number, and source URL.
   - If reliable evidence is absent from the local repository, the system outputs an **Insufficient Evidence Notice** rather than fabricating legal facts.

