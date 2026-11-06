# NYAYASETU REST API Documentation

This document describes all REST API endpoints available in **NYAYASETU — An AI-Assisted, Evidence-Oriented Judicial Information Platform**.

Base URL: `http://localhost:8000/api`

---

## 1. System Health

### `GET /api/health/`
Returns system status, active version, and service catalog.
- **Auth:** Public
- **Response:**
  ```json
  {
    "platform": "NYAYASETU",
    "tagline": "An AI-Assisted, Evidence-Oriented Judicial Information Platform",
    "status": "healthy",
    "version": "1.0.0",
    "endpoints": { ... }
  }
  ```

---

## 2. Authentication

### `POST /api/auth/register/`
Registers a new Citizen account.
- **Auth:** Public
- **Payload:**
  ```json
  {
    "username": "ramesh_kumar",
    "email": "ramesh@example.com",
    "password": "securepassword123",
    "first_name": "Ramesh",
    "last_name": "Kumar"
  }
  ```

### `POST /api/auth/login/`
Authenticates user and returns JWT tokens.
- **Auth:** Public
- **Payload:**
  ```json
  {
    "username": "ramesh_kumar",
    "password": "securepassword123"
  }
  ```
- **Response:**
  ```json
  {
    "access": "<JWT_ACCESS_TOKEN>",
    "refresh": "<JWT_REFRESH_TOKEN>"
  }
  ```

### `POST /api/auth/refresh/`
Refreshes an expired access token.
- **Auth:** Public
- **Payload:** `{"refresh": "<JWT_REFRESH_TOKEN>"}`

### `GET /api/auth/me/`
Returns current user's profile and assigned role (`CITIZEN` or `ADMIN`).
- **Auth:** Bearer Token

---

## 3. Hybrid Judicial Search

### `GET /api/search/?q=<query>`
Executes hybrid keyword and pgvector cosine semantic search across 2,058 dense BGE embeddings.
- **Auth:** Public
- **Query Parameters:**
  - `q` (required): Search query text
  - `court_id` (optional): Filter by court ID
  - `case_type` (optional): Filter by case type (e.g. `Criminal Appeal`)
  - `year` (optional): Filter by judgment year (e.g. `2023`)
  - `document_type` (optional): `JUDGMENT`, `FINAL_ORDER`, etc.
  - `top_k` (optional, default `10`, max `50`): Number of results
  - `alpha` (optional, default `0.5`): Balance between keyword (`1.0`) and semantic (`0.0`)
- **Response:**
  ```json
  {
    "query": "child witness testimony",
    "count": 10,
    "results": [
      {
        "chunk_id": 84,
        "case_id": 2,
        "case_number": "2023 INSC 599",
        "case_title": "Pradeep v. State of Haryana",
        "document_id": 2,
        "document_title": "Judgment in Pradeep v State of Haryana",
        "page_number": 3,
        "snippet": "...corroboration of child witness testimony...",
        "keyword_score": 0.85,
        "semantic_score": 0.89,
        "hybrid_score": 0.87,
        "source_url": "https://..."
      }
    ]
  }
  ```

---

## 4. Case Dossier & Timelines

### `GET /api/cases/cases/`
Lists public judicial cases with pagination and filtering.
- **Auth:** Public

### `GET /api/cases/cases/<id>/`
Returns full case detail including bench coram, parties, citations, timeline events, and documents.
- **Auth:** Public

### `GET /api/cases/<id>/related/`
Returns explainable related precedents with explicit legal relationship reasons.
- **Auth:** Public
- **Response:**
  ```json
  {
    "case_id": 2,
    "case_number": "2023 INSC 599",
    "related_cases": [
      {
        "id": 15,
        "case_number": "AIR 1973 SC 225",
        "case_title": "Kesavananda Bharati v. State of Kerala",
        "relationship_type": "CITES",
        "reason": "Directly cited as precedent in judgment"
      }
    ]
  }
  ```

### `GET /api/search/cases/<id>/timeline/`
Returns verified chronological procedural events for a case.
- **Auth:** Public

---

## 5. Evidence-Grounded AI Assistant

### `POST /api/assistant/`
Submits a legal inquiry to the evidence-grounded assistant.
- **Auth:** Public
- **Payload:**
  ```json
  {
    "query": "What was held regarding child witness testimony in Pradeep v State of Haryana?",
    "top_k": 5,
    "alpha": 0.5
  }
  ```
- **Response:**
  ```json
  {
    "query": "What was held regarding child witness testimony in Pradeep v State of Haryana?",
    "answer": "In Pradeep v. State of Haryana (2023 INSC 599), the Supreme Court reiterated...",
    "has_sufficient_evidence": true,
    "evidence": [
      {
        "case_number": "2023 INSC 599",
        "case_title": "Pradeep v. State of Haryana",
        "page_number": 3,
        "source_url": "https://..."
      }
    ],
    "disclaimer": "NYAYASETU provides informational assistance based on available judicial records..."
  }
  ```

---

## 6. Judicial Knowledge Graph

### `GET /api/graph/cases/<id>/`
Returns graph nodes and relationships for a case. Tries Neo4j first, with fallback to the PostgreSQL derived graph model.
- **Auth:** Public
- **Response:**
  ```json
  {
    "case_id": 2,
    "case_number": "2023 INSC 599",
    "nodes": [
      { "id": "case_2", "type": "Case", "label": "2023 INSC 599" },
      { "id": "court_1", "type": "Court", "label": "Supreme Court of India" },
      { "id": "judge_5", "type": "Judge", "label": "Hon'ble Justice..." }
    ],
    "links": [
      { "source": "case_2", "target": "court_1", "type": "FILED_IN", "label": "Filed In" },
      { "source": "case_2", "target": "judge_5", "type": "HEARD_BY", "label": "Heard By" }
    ],
    "textual_relationships": [
      "Filed in Supreme Court of India",
      "Heard by Judge ..."
    ],
    "source": "neo4j"
  }
  ```

### `GET /api/graph/status/`
Checks Neo4j database connectivity and configuration.

### `POST /api/graph/sync/`
Synchronizes PostgreSQL judicial records to Neo4j using idempotent MERGE.
- **Auth:** Admin only (`role: ADMIN`)

---

## 7. Private Document Vault

### `GET /api/documents/user-documents/`
Lists current citizen's uploaded private documents. Enforces strict multi-tenant isolation.
- **Auth:** Bearer Token

### `POST /api/documents/user-documents/`
Uploads a private PDF document for text extraction and chunking.
- **Auth:** Bearer Token
- **Payload:** `multipart/form-data` with `file` (.pdf) and optional `title`.

### `GET /api/documents/user-documents/<id>/`
Returns user document detail and extracted text.
- **Auth:** Bearer Token (must own document)

### `GET /api/documents/user-documents/<id>/summary/`
Returns summary and chunk count of user document.
- **Auth:** Bearer Token (must own document)

### `DELETE /api/documents/user-documents/<id>/`
Deletes user document and associated chunks.
- **Auth:** Bearer Token (must own document)

---

## 8. Judicial Services Directory

### `GET /api/services/services/`
Returns verified official government and judicial portals.
- **Auth:** Public
- **Query Parameters:** `category` (`LEGAL_AID`, `CASE_STATUS`, `E_FILING`, `CONSUMER_FORUM`, `TRAFFIC_CHALLAN`)

---

## 9. Admin Platform Metrics

### `GET /api/admin/stats/`
Returns counts of cases, courts, judges, parties, documents, chunks, uploads, and users.
- **Auth:** Admin only (`role: ADMIN`)

