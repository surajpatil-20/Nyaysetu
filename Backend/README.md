# NYAYASETU — Backend Intelligence Pipeline

**An AI-Assisted, Evidence-Oriented Judicial Information Platform**

Final-Year B.Tech CSE (Data Science) Mega Project

---

## 1. Core Operating Principles

NYAYASETU is a citizen-centric, evidence-oriented judicial information retrieval platform.

### What NYAYASETU IS:
- A search and discovery platform for public judicial records, cases, courts, and acts.
- A semantic information assistance layer grounded strictly in retrieved judicial text.
- A timeline and relationship visualizer for judicial proceedings.
- Transparent with respect to source provenance, court names, and document citations.

### What NYAYASETU IS NOT:
- **NOT a lawyer or legal representative**: Does not provide legal counsel, litigation strategy, or legal advice.
- **NOT a judge or decision-maker**: Makes no judicial determinations or rulings.
- **NOT an outcome prediction system**: Never computes "win probabilities" or predicts case verdicts.
- **NOT a judge prediction system**: Does not profile judges or forecast their individual rulings.
- **NOT a hallucinated generator**: If retrieved evidence is insufficient, the system explicitly reports insufficient evidence rather than guessing.

---

## 2. Intelligence Pipeline Architecture

```text
STEP 2: Data Ingestion
        ↓
  Clean + Validate Data (CNR, Courts, Dates, Status)
        ↓
  Store Cases / Courts / Judges / Parties / Sources
        ↓
STEP 3: PDF Document Processing
        ↓
  PyMuPDF Text Extraction + Cleaning + Page-Aware Structuring
        ↓
STEP 4: Chunking + Dense Embeddings
        ↓
  Paragraph-Boundary Overlapping Chunks (500–800 tokens)
  768-dim Sentence Embeddings (BAAI/bge-base-en-v1.5)
        ↓
STEP 5: Hybrid Search
        ↓
  PostgreSQL Keyword Coverage + Dense Vector Cosine Similarity
  Score Fusion: score = α · keyword + (1 - α) · semantic
        ↓
STEP 6: Evidence-Grounded RAG Assistant
        ↓
  Strict System Prompt + Grounded Context Injection
  Verifiable [Evidence N] Citations + Mandatory Legal Disclaimer
```

---

## 3. Technology Stack

- **Runtime**: Python 3.12
- **Framework**: Django 6.1.2 + Django REST Framework 3.18.3
- **Primary Database**: PostgreSQL 18 (Localhost:5432)
- **Vector Backend**: Native PostgreSQL `pgvector` 0.8.6 extension (`vector(768)` with HNSW cosine distance index)
- **PDF Extraction & OCR**: PyMuPDF (`fitz` / `pymupdf` 2.1) + built-in Tesseract C-API integration with `eng.traineddata`
- **Embeddings**: Sentence-Transformers / 768-dim dense embedding vectors (`BAAI/bge-base-en-v1.5`)
- **LLM Abstraction**: Pluggable provider architecture (`mock`, `gemini`, `openai`, `groq`, `ollama`)

---

## 4. Setup & Environment Configuration

### Prerequisites
- Python 3.12 virtualenv: `.\venv\Scripts\activate`
- PostgreSQL 15+ running on `localhost:5432` with database `nyaysetu`

### Environment Variables (.env)
```env
DEBUG=True
SECRET_KEY=your-secure-django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

DB_ENGINE=django.db.backends.postgresql
DB_NAME=nyaysetu
DB_USER=suraj
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

EMBEDDING_MODEL_NAME=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSION=768

LLM_PROVIDER=mock       # mock | gemini | openai
LLM_MODEL=gemini-1.5-flash
LLM_API_KEY=your_gemini_api_key_here
```

---

## 5. Management Commands Quick Reference

### Ingestion Commands (`apps/data_ingestion`)
```bash
# Validate dataset without writing to DB
python manage.py validate_dataset --file data/raw/demo_cases.csv
python manage.py validate_dataset --file data/raw/demo_cases.json

# Dry-run import
python manage.py import_cases --file data/raw/demo_cases.csv --dry-run

# Execute idempotent case import
python manage.py import_cases --file data/raw/demo_cases.csv
```

### Document Processing Commands (`apps/documents`)
```bash
# Import a single PDF and link to an existing Case
python manage.py import_documents --file data/documents/demo_judgment_1234.pdf --case-number "W.P.(C) 1234/2023" --title "Final Judgment" --process --embed

# Batch process documents (text extraction & chunking)
python manage.py process_documents --limit 10

# Generate 768-dim embeddings for un-embedded chunks
python manage.py generate_embeddings

# Wipe and rebuild all embeddings
python manage.py rebuild_embeddings
```

---

## 6. REST API Reference

### Health Check
- **`GET /api/health/`**
  - Returns platform status and registered subsystem endpoints.

### Hybrid Search
- **`GET /api/search/?q=<query>`**
  - Parameters:
    - `q` (required): Search terms or natural language query.
    - `court_id` (optional): Filter by court.
    - `case_type` (optional): e.g. `Writ Petition`.
    - `year` (optional): Filter by decision/filing year.
    - `top_k` (optional, default 10): Number of results.
    - `alpha` (optional, default 0.5): Keyword weight vs. semantic weight.
  - Returns: Array of `EvidenceResult` with `chunk_id`, `case_number`, `document_title`, `page_number`, `snippet`, `hybrid_score`, `source_name`, `source_url`.

### Case Timeline
- **`GET /api/search/cases/<case_id>/timeline/`**
  - Returns chronological procedural milestones (`FILED`, `HEARING`, `ORDER`, `JUDGMENT`).

### Evidence-Grounded Assistant (RAG)
- **`POST /api/assistant/`**
  - Body:
    ```json
    {
      "query": "What did the court hold regarding equality before law under Article 14?",
      "top_k": 5,
      "alpha": 0.5
    }
    ```
  - Response:
    ```json
    {
      "query": "What did the court hold regarding equality before law under Article 14?",
      "answer": "Based strictly on the judicial records retrieved from the NYAYASETU repository:\n\n- [Evidence 1]: In Ramesh Kumar v. Union of India...",
      "has_sufficient_evidence": true,
      "evidence_count": 2,
      "sources": [
        {
          "citation_tag": "[Evidence 1]",
          "chunk_id": 1,
          "case_id": 1,
          "case_number": "W.P.(C) 1234/2023",
          "case_title": "Ramesh Kumar v. Union of India",
          "document_id": 2,
          "document_title": "Final Judgment in W.P.(C) 1234/2023",
          "page_number": 1,
          "snippet": "...",
          "relevance_score": 0.5,
          "source_name": "DEMO SOURCE",
          "source_url": null
        }
      ],
      "disclaimer": "Disclaimer: NYAYASETU is an AI-assisted judicial information tool designed for citizen awareness and research. It does not provide legal advice, legal opinions, case outcome forecasts, or lawyer representation. For legal disputes or formal proceedings, consult a qualified advocate or the official court registry."
    }
    ```

---

## 7. Automated Test Suite

Run all 42 tests across the four intelligence pipeline applications:

```bash
python manage.py test apps.data_ingestion apps.documents apps.search apps.assistant --noinput
```

All 42 test cases cover:
- CSV & JSON format validation, missing fields, duplicate handling, and dry-run execution
- PDF text extraction, whitespace cleanup, tokenization, paragraph boundary chunking, and ordering
- PyMuPDF native OCR extraction on scanned image documents
- Native `VectorField(dimensions=768)` persistence and dimension enforcement
- PostgreSQL pgvector database-level `CosineDistance` query and HNSW index execution
- Hybrid search scoring, stop-word tokenization, term coverage, filters, and empty query handling
- Assistant RAG prompt formatting, Mock LLM synthesis, source citation structuring, insufficient evidence handling, and REST API validation.

