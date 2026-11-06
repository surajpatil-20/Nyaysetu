# NYAYASETU
### AI-Assisted, Evidence-Oriented Judicial Information Platform

> **Civic & Legal Notice:** NYAYASETU provides informational assistance based on available judicial records. It does **NOT** provide legal advice, does **NOT** predict judicial outcomes, does **NOT** predict judge behaviors or winning probabilities, and does **NOT** make judicial decisions. Always consult a licensed advocate for legal counsel.

---

## 1. Project Overview

**NYAYASETU** is an open, evidence-grounded judicial intelligence platform designed to democratize access to Indian case law for citizens, researchers, and legal practitioners.

Built on genuine records from the **Indian Supreme Court Judgments Open Dataset** (1950–2025, licensed under **CC BY 4.0**), the system combines relational data, vector search, knowledge graphs, and RAG to ensure that every answer, citation, and summary is traceable to an official public court record.

---

## 2. End-to-End Architecture

```text
       REAL JUDICIAL DATA (AWS Open Data / Supreme Court of India, CC BY 4.0)
                                      ↓
           PostgreSQL 15+ (Relational Source of Truth + pgvector extension)
                                      ↓
           Document Processing (PyMuPDF Text Extraction + Tesseract OCR Fallback)
                                      ↓
         Paragraph-Aware Chunking → Dense Embeddings (BAAI/bge-base-en-v1.5)
                                      ↓
           HNSW Cosine Vector Index (768-dim, vector_cosine_ops)
                                      ↓
      ┌───────────────────────────────┴───────────────────────────────┐
      ↓                                                               ↓
Hybrid Search Service (pgvector + ILIKE)               Judicial Knowledge Graph (Neo4j / Derived)
      ↓                                                               ↓
Evidence-Grounded RAG Assistant (w/ Insufficient Safeguard)     Case & Precedent Relationships
      └───────────────────────────────┬───────────────────────────────┘
                                      ↓
                        Django REST Framework APIs + JWT Auth
                                      ↓
                     React 19 + Vite + React Router Frontend
```

---

## 3. Technology Stack

- **Backend Framework:** Django 6.1.2 + Django REST Framework 3.15+
- **Primary Database:** PostgreSQL 15+ with `pgvector` 0.8.6+ extension
- **Vector Index:** PostgreSQL HNSW index on `DocumentChunk.embedding` (Cosine Similarity, 768 dimensions)
- **Embedding Model:** `BAAI/bge-base-en-v1.5` via `sentence-transformers`
- **Document Processing:** PyMuPDF (`pymupdf`) with Tesseract OCR fallback
- **Knowledge Graph:** Neo4j (Cypher `MERGE` idempotent sync + PostgreSQL derived fallback)
- **Authentication:** JWT via `djangorestframework-simplejwt`
- **Frontend Framework:** React 19 + Vite 8 + React Router 7 + Tailwind CSS

---

## 4. Real Judicial Dataset & Licensing

- **Dataset:** Indian Supreme Court Judgments Open Dataset
- **Authority:** Supreme Court of India public judgments (1950–2025)
- **Host:** Registry of Open Data on AWS (`s3://indian-supreme-court-judgments/`)
- **License:** Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))
- **Production Records:** 100 genuine Supreme Court judgments, 100 PDFs, 2,058 document chunks, and 2,058 normalized dense vectors.
- **Zero Paid Dependencies:** No paid legal databases (SCC Online, Manupatra) or proprietary APIs required.

---

## 5. Prerequisites & Environment Setup

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- PostgreSQL 15+ with `pgvector` installed (`CREATE EXTENSION IF NOT EXISTS vector;`)
- (Optional) Neo4j 5+ instance running at `bolt://localhost:7687`

---

## 6. Backend Setup

```powershell
# 1. Navigate to Backend directory
cd Backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your PostgreSQL credentials (DB_NAME, DB_USER, DB_PASSWORD)

# 5. Apply migrations
python manage.py migrate

# 6. Seed official judicial services
python manage.py seed_services

# 7. (Optional) Run Knowledge Graph sync to Neo4j
python manage.py sync_knowledge_graph --dry-run
python manage.py sync_knowledge_graph
```

---

## 7. Frontend Setup

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
copy .env.example .env

# 4. Build frontend for production
npm run build

# 5. Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## 8. Running the Backend Server

```powershell
cd Backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

The REST API will be available at `http://localhost:8000/api/`.

---

## 9. Running Tests

The test suite covers data ingestion, document processing, pgvector hybrid search, RAG assistant safeguards, case relationships, knowledge graph, services, and private document tenant isolation:

```powershell
cd Backend
.\venv\Scripts\Activate.ps1
python manage.py test --noinput
```
*Current test status: 64/64 tests passing.*

---

## 10. Core REST API Endpoints

| Category | Endpoint | Description |
|---|---|---|
| **Health** | `GET /api/health/` | System status & catalog |
| **Auth** | `POST /api/auth/register/` | Citizen registration |
| **Auth** | `POST /api/auth/login/` | JWT token acquisition |
| **Auth** | `GET /api/auth/me/` | Current user profile |
| **Search** | `GET /api/search/?q=<query>` | Hybrid pgvector + keyword search |
| **Cases** | `GET /api/cases/cases/<id>/` | Comprehensive case detail & coram |
| **Cases** | `GET /api/cases/<id>/related/` | Explainable related precedents |
| **Timeline** | `GET /api/search/cases/<id>/timeline/` | Chronological procedural events |
| **Assistant** | `POST /api/assistant/` | Evidence-grounded AI consultation |
| **Graph** | `GET /api/graph/cases/<id>/` | Case knowledge graph nodes & links |
| **Graph** | `POST /api/graph/sync/` | Sync records to Neo4j (Admin) |
| **Vault** | `POST /api/documents/user-documents/` | Upload private PDF document |
| **Services**| `GET /api/services/services/` | Official government portal registry |
| **Admin** | `GET /api/admin/stats/` | Platform metrics & health diagnostics |

---

## 11. Final Demonstration Flow

1. **Search Cases:** Open `/search` and query `"child witness testimony"`.
2. **Inspect Precedent:** Select *Pradeep v. State of Haryana* (`2023 INSC 599`). View bench coram, parties, and judgment PDF.
3. **Explore Knowledge Graph:** Navigate to `/cases/<id>/graph` to inspect nodes (Case, Court, Judge, Party, Act, Section) and verified textual relationships.
4. **Grounded AI Assistant:** Open `/assistant` and ask *"What was held regarding child witness testimony in Pradeep v State of Haryana?"*. Observe evidence provenance cards with exact page citations.
5. **Safety Safeguard:** Ask *"What is the chemical structure of chlorophyll?"*. Observe the **Insufficient Evidence Notice** without hallucinations.
6. **Private Document Vault:** Sign in as a citizen, upload a private legal PDF at `/documents`, and verify multi-tenant isolation.
7. **Judicial Services:** Open `/services` to access official NALSA, eCourts, and e-Filing portals.

