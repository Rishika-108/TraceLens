# TraceLens: AI-Assisted Digital Forensics Intelligence Platform

<p align="center">
  <img src="Client/src/assets/hero.png" alt="TraceLens Hero" width="800" />
</p>

<p align="center">
  <strong>Grounded Digital Evidence Ingestion, Chronological Timeline Reconstruction, Forensic Graph Analytics & Explainable RAG Investigation</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19.2+-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-v4.3-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-384--dim-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Pytest-30%20Passed-4CAF50?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/Chain_of_Custody-SHA--256-blue?style=for-the-badge&logo=securityscorecard&logoColor=white" />
</p>

---

## Table of Contents
1. [Project Brief](#1-project-brief)
2. [Why This Project Exists](#2-why-this-project-exists)
3. [Engineering Highlights & Technical System Design](#3-engineering-highlights--technical-system-design)
4. [Architecture & Data Flow](#4-architecture--data-flow)
5. [Core Operational Workflow](#5-core-operational-workflow)
6. [System Specs & Numerical Metrics Summary](#6-system-specs--numerical-metrics-summary)
7. [Technology Stack](#7-technology-stack)
8. [Local Support & Setup Guide](#8-local-support--setup-guide)
9. [Automated Testing & Quality Assurance Suite](#9-automated-testing--quality-assurance-suite)

---

## 1. Project Brief

**TraceLens** is an open-source, full-stack digital forensics intelligence platform engineered for law enforcement agencies, cybercrime investigators, forensic auditors, and incident response teams.

TraceLens ingests heterogeneous, unstructured digital evidence—including **WhatsApp chat exports, call detail records (CDRs), SMS archives, RFC 822 email files, browser SQLite databases, documents, and EXIF image metadata**—and automatically:
- **Computes SHA-256 cryptographic hashes** in real-time streams to preserve chain of custody.
- **Normalizes disparate timestamps** (WebKit microseconds, Unix epochs, 12h/24h formats) into a unified chronological timeline.
- **Extracts multi-type forensic entities** (Suspects, Phone numbers, Emails, Bitcoin/Ethereum wallets, IP addresses, Locations) with unbreakable provenance back to raw artifact bytes.
- **Discovers suspect-to-suspect communication graphs** with calibrated confidence scoring.
- **Generates 384-dimensional dense vector embeddings** indexed in `pgvector` for semantic similarity search.
- **Provides an Explainable AI Investigation Agent** that strictly separates observed `[FACT]` from analytical `[INFERENCE]`, provides mandatory evidence citations (`[Artifact #<id>]`), and acknowledges insufficient evidence when records are absent.
- **Synthesizes court-admissible Case Intelligence Reports** with 1-click printable/PDF exports.

---

## 2. Why This Project Exists

Modern digital forensics investigations face four critical bottlenecks:

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ Heterogeneous Data Silos │    │ Chain of Custody Leaks  │    │ AI Hallucination Risks  │
│  (Chat, Calls, Web,     │ ── │  (Unverified files,     │ ── │  (Black-box LLMs making │
│   EML, SQLite, Images)  │    │   lost byte provenance) │    │   unsupported claims)   │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

1. **Massive Cognitive Overload & Data Fragmentation**: A single investigation routinely involves gigabytes of unstructured WhatsApp chats, thousands of call log rows, hundreds of `.eml` emails, and SQLite browser histories across multiple devices. Investigators lose hundreds of hours manually cross-referencing timestamps and phone numbers.
2. **Chain of Custody & Evidence Tampering Risks**: Digital evidence presented in court requires cryptographic verification. If an analytical platform modifies files during processing or cannot trace a derived entity back to its exact byte offset in raw evidence, the evidence risks being thrown out.
3. **The AI Hallucination Crisis in Law Enforcement**: General-purpose LLMs hallucinate facts, make unverified claims, and invent plausible-sounding details. In forensic science, a hallucinated phone number or fabricated timeline event can destroy an investigation.
4. **Cross-Case Data Contamination**: Multi-tenant or multi-case systems must guarantee absolute mathematical case isolation. Evidence from Case A must never bleed into vector similarity searches or RAG contexts of Case B.

### How TraceLens Solves This
TraceLens enforces **6 Non-Negotiable Forensic Invariants**:
- **Invariant 1 (Evidence Supremacy)**: The raw evidence file is the single source of truth.
- **Invariant 2 (Cryptographic Custody)**: Every file is hashed with streaming SHA-256 before ingestion.
- **Invariant 3 (Fact vs. Inference Separation)**: Directly observed records are labeled `[FACT]`; deductions are labeled `[INFERENCE]`.
- **Invariant 4 (Mandatory Provenance)**: Every claim, entity, and report entry cites its originating `[Artifact #<id>]`.
- **Invariant 5 (Insufficient Evidence Awareness)**: The AI explicitly declares `INSUFFICIENT EVIDENCE` with `0.0` confidence if facts are missing.
- **Invariant 6 (Case Isolation)**: All database queries, vector similarity lookups, and graph traversals are strictly scoped by `case_id`.

---

## 3. Engineering Highlights & Technical System Design

### A. Streaming Forensic Ingestion & SHA-256 Checksums
Instead of loading entire multi-gigabyte evidence files into RAM, `StorageService` streams bytes in 64KB chunks directly into case-isolated storage directories (`storage/evidence/{case_id}/`) while calculating the cryptographic SHA-256 hash in the same I/O pass.

### B. Robust Multi-Format Forensic Parsers
| Parser Module | Supported Formats | Forensic Capabilities |
| :--- | :--- | :--- |
| **`WhatsAppParser`** | `.txt` (Android & iOS) | Regex tokenizer handling multiline messages, 12h/24h timestamps, comma/dash separators, and system/media notices. |
| **`CallParser`** | `.csv`, `.json` | Flexible header discovery (`caller`, `receiver`, `duration`), direction normalization (`INCOMING`, `OUTGOING`, `MISSED`, `REJECTED`). |
| **`SMSParser`** | `.csv`, `.json` | Flexible column sniffing (`sender`, `recipient`, `message`, `body`), direction resolution. |
| **`EmailParser`** | `.eml`, `.json` | RFC 822 MIME parsing via Python standard library, header extraction (`From`, `To`, `Cc`, `Subject`, `Date`), body decoding, and attachment metadata. |
| **`BrowserParser`** | SQLite, `.csv`, `.json` | Direct query of Chrome/Edge/Firefox SQLite `History` databases (`urls` and `visits` tables) with WebKit/Unix microsecond conversion. |
| **`DocumentParser`** | `.pdf`, `.txt`, `.md` | Page-by-page PDF extraction via `pypdf` with section numbering and paragraph chunking. |
| **`ImageParser`** | `.jpg`, `.jpeg`, `.png` | EXIF metadata extraction via `Pillow` (Camera make/model, timestamps, GPS coordinates, dimensions). |

### C. Multi-Type Entity Extraction Engine
Extracts structured forensic entities from both structured fields and unstructured text payloads:
- **Phone Numbers**: International (`+1 415 555 2671`, `+91-9876543210`) and regional formats.
- **Email Addresses**: RFC-compliant email regex.
- **Cryptocurrency Wallets**: Bitcoin (P2PKH `1...`, P2SH `3...`, Bech32 `bc1...`) and Ethereum (`0x...` 40 hex chars).
- **Network IOCs**: IPv4 addresses, domains, and hostnames.
- **Organizations & Locations**: Bank names (`Zurich Bank`, `Swiss Bank`), government bodies (`FBI`, `Interpol`), roads, and cities.
- **Provenance Linkage**: Every entity is bound to `artifact_id` and `case_id`.

### D. Evidence-Grounded Relationship Discovery
Replaces naive cross-products with evidentiary link analysis:
- **Direct Communications**: `CALLS`, `MESSAGES`, `EMAILS`, `CHATS_WITH` with high baseline confidence (`0.90` + frequency scaling).
- **Artifact Co-occurrences**: Entities appearing in the same message/document with co-occurrence confidence weighting (`0.70` + frequency scaling).

### E. Case-Isolated pgvector RAG & Semantic Retrieval
- Generates 384-dimensional vector embeddings using `SentenceTransformer("all-MiniLM-L6-v2")` with local model caching and fast unit-normalized deterministic fallback for air-gapped/offline test environments.
- Vector similarity search executes cosine distance queries (`1.0 - Artifact.embedding.cosine_distance(query_embedding)`) joined with `Evidence.case_id == case_id`.

### F. Context Builder & Grounded Investigation Agent
The **Context Builder** formats retrieved artifacts with unambiguous headers:
```
[EVIDENCE_REF #1 | ID: art-99 | TYPE: WHATSAPP_MESSAGE | TIMESTAMP: 2023-08-15 15:00:00]
  sender: Mastermind
  message: Transfer the 250000 USD to Account #99881 at Zurich Bank.
  Raw Snippet: 15/08/2023, 15:00 - Mastermind: Transfer the 250000 USD...
```
The **Investigation Agent** parses the context and returns structured findings:
- `### Executive Summary` (Direct answer with confidence percentage).
- `### Evidence-Backed Findings` (Strict separation of `[FACT]` and `[INFERENCE]`).
- `### Supporting Evidence References` (List of artifact IDs and timestamps).
- `### Identified Gaps / Uncertainties` (Missing records, unverified aliases).

### G. Centralized Safe Logging with Evidence Redaction
To prevent sensitive suspect communication records from leaking into log aggregators (AGENT.md Sec. 23 & 69), `core/logging.py` implements an `EvidenceRedactionFilter` that intercepts all log records and redacts phone numbers, email addresses, and crypto wallet addresses while preserving operational telemetry (`case_id`, `evidence_id`, `status`).

---

## 4. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Client["Frontend Workspace (React 19 + Vite 8 + Tailwind v4)"]
        UI_Dash[Case Portfolio Dashboard]
        UI_Upload[Evidence Ingestion Dropzone]
        UI_Timeline[Chronological Timeline Explorer]
        UI_Graph[ReactFlow Relationship Graph]
        UI_Entities[Forensic Entity Directory]
        UI_Search[pgvector Semantic Search]
        UI_Agent[AI Investigation Console]
        UI_Report[Case Intelligence Report Studio]
    end

    subgraph API["FastAPI Gateway (Port 8000)"]
        R_Auth["/api/auth (JWT & RBAC)"]
        R_Case["/api/cases"]
        R_Ev["/api/evidence/upload"]
        R_Intel["/api/timelines, /api/entities, /api/relationships"]
        R_Search["/api/search"]
        R_Inv["/api/investigations"]
        R_Rep["/api/reports"]
    end

    subgraph Pipeline["Ingestion & Intelligence Pipelines"]
        P_Hash[Streaming SHA-256 Checksum]
        P_Parse[8 Multi-Format Forensic Parsers]
        P_Norm[Standardized Normalizer]
        P_Ent[Entity Extraction Engine]
        P_Rel[Relationship Discovery Builder]
        P_Time[Timeline Reconstruction]
        P_Emb[384-Dim Embedding Generator]
    end

    subgraph Database["Storage & Data Layer"]
        DB_Meta[(PostgreSQL / SQLite Metadata)]
        DB_Vec[(pgvector 384-Dim Embeddings)]
        Storage[(Secure File Storage: storage/evidence/)]
    end

    Client -->|REST + Bearer JWT| API
    R_Ev --> P_Hash --> Storage
    P_Hash --> P_Parse --> P_Norm --> P_Ent --> P_Rel --> P_Time --> P_Emb
    P_Emb --> DB_Vec
    P_Norm --> DB_Meta
    R_Search --> DB_Vec
    R_Inv --> DB_Vec
    R_Rep --> DB_Meta
```

---

## 5. Core Operational Workflow

```
1. Authenticate Investigator
   └─► POST /api/auth/login ──► Returns JWT Access Token (HS256)

2. Create Forensic Case
   └─► POST /api/cases/ ────► Creates isolated case record & storage directory

3. Ingest Multi-Source Evidence
   └─► POST /api/evidence/upload (multipart/form-data)
       ├─► Compute SHA-256 hash & save raw file
       ├─► Sniff & invoke parser (WhatsApp, Calls, SMS, EML, SQLite, Docs)
       ├─► Extract entities & discover relationships
       ├─► Build chronological timeline events
       └─► Generate 384-dim dense embeddings & index in pgvector

4. Intelligence Visualizations
   ├─► Timeline Explorer ───► Filter by Call, Chat, SMS, Email, Web, Doc
   ├─► ReactFlow Graph ────► Interactive suspect-to-suspect communication network
   └─► Entity Directory ───► Copy-to-clipboard phone numbers, emails, crypto wallets

5. Semantic Vector Search
   └─► POST /api/search/ ──► Natural language query across vector space

6. AI Investigation Agent
   └─► POST /api/investigations/
       ├─► Context Builder gathers top-k artifacts
       ├─► RAG reasoning with [FACT] vs [INFERENCE] tags
       └─► Mandatory [Artifact #<id>] citations

7. Generate Case Intelligence Report
   └─► POST /api/reports/generate ──► Formal report with PDF/Print export
```

---

## 6. System Specs & Numerical Metrics Summary

| Dimension | Specification / Metric | Description |
| :--- | :--- | :--- |
| **Vector Embedding Dimension** | `384` dimensions | SentenceTransformer (`all-MiniLM-L6-v2`) with cosine distance |
| **Cryptographic Hashing** | `SHA-256` (64 hex chars) | Streaming byte hashing per evidence file for chain of custody |
| **Password Hashing** | `PBKDF2-HMAC-SHA256` | 100,000 iterations with 16-byte cryptographically secure salt |
| **Token Standard** | `JWT (RFC 7519)` | HS256 algorithm with configurable expiration |
| **Forensic Parsers** | `8` modules | WhatsApp, Calls, SMS, Emails (EML), Browser SQLite, PDF, Text, EXIF |
| **Entity Types Extracted** | `8` categories | `PERSON`, `PHONE`, `EMAIL`, `CRYPTO_ADDRESS`, `IP_ADDRESS`, `ORG`, `LOCATION`, `DOMAIN` |
| **Relationship Confidence** | `0.50` to `0.99` | Dynamically scaled based on communication channel and frequency |
| **Backend Test Suite** | `30 / 30 Passed (100%)` | Pytest coverage across parsers, pipelines, storage, AI routes, and security |
| **Frontend Production Build** | `1.32s` | Vite 8 + Rollup bundle compilation with zero errors |
| **Default Server Port** | `8000` | FastAPI / Uvicorn ASGI Server |
| **Default Client Port** | `3000` / `5173` | Vite Dev Server |

---

## 7. Technology Stack

### Backend
- **Core Framework**: Python 3.10+, FastAPI (ASGI), Pydantic v2, Pydantic-Settings
- **Database & ORM**: PostgreSQL with `pgvector` extension, SQLAlchemy 2.0, SQLite (in-memory test engine)
- **Asynchronous Task Queue**: Celery, Redis
- **AI & NLP**: `sentence-transformers`, `torch`, `google-genai` (Gemini 2.5 Flash), `openai` (GPT-4o mini)
- **Forensic Extraction**: `pypdf` (PDFs), `Pillow` (EXIF image metadata), `python-dateutil` (datetime parsing), `sqlite3` (browser history databases)
- **Security & Logging**: `hashlib`, `hmac`, `jwt`, custom `EvidenceRedactionFilter`
- **Testing**: `pytest`, `pytest-asyncio`, `httpx` (FastAPI TestClient)

### Frontend
- **Core Framework**: React 19, Vite 8, JavaScript (ESNext)
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite`), Custom Glassmorphism System
- **Graph Visualization**: `reactflow` (node-link network graph, MiniMap, Controls)
- **State Management & Routing**: React Context (`AuthContext`, `CaseContext`), `react-router-dom` v7
- **HTTP Client**: Axios with automatic Bearer token injection
- **File Ingestion**: `react-dropzone` (drag-and-drop file upload)
- **Icons & Alerts**: `react-icons` (Feather Icons), `react-toastify`

---

## 8. Local Support & Setup Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher (with `npm`)
- PostgreSQL 15+ with `pgvector` extension (Optional; SQLite in-memory fallback is supported for local evaluation)
- Redis (Optional; for asynchronous Celery workers)

---

### A. Backend Setup & Startup

1. **Navigate to the Server directory**:
   ```powershell
   cd Server
   ```

2. **Create and activate a Python virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # On Windows PowerShell
   # source venv/bin/activate    # On Linux/macOS
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in `Server/` (a sample is provided):
   ```env
   APP_NAME=TraceLens
   APP_VERSION=1.0.0
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tracelens
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=tracelens-super-secret-cryptographic-key-2026
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   STORAGE_PATH=./storage
   ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   VECTOR_DIMENSION=384
   # Optional LLM API Keys (Falls back to deterministic rule-based engine if omitted):
   # GEMINI_API_KEY=your_gemini_api_key
   # OPENAI_API_KEY=your_openai_api_key
   ```

5. **Start the FastAPI Backend Server**:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

6. **(Optional) Start the Celery Background Task Worker**:
   ```powershell
   celery -A app.tasks.celery_app worker --loglevel=info -P solo
   ```

---

### B. Frontend Setup & Startup

1. **Navigate to the Client directory**:
   ```powershell
   cd Client
   ```

2. **Install dependencies**:
   ```powershell
   npm install
   ```

3. **Start the Vite development server**:
   ```powershell
   npm run dev
   ```
   Open your browser at [http://localhost:3000](http://localhost:3000) or [http://localhost:5173](http://localhost:5173).

---

## 9. Automated Testing & Quality Assurance Suite

TraceLens includes an extensive automated test suite covering all forensic parsers, ingestion pipelines, storage services, vector search, investigation RAG reasoning, report generation, authentication, and safe logging.

### Running the Test Suite
From the `Server/` directory:
```powershell
.\venv\Scripts\python.exe -m pytest tests -p no:logfire -v
```

### Test Suite Execution Matrix (30 Tests, 100% Pass Rate)

| Test Module | Tests | Focus Area | Status |
| :--- | :---: | :--- | :---: |
| **`test_auth_and_security.py`** | 5 | PBKDF2 hashing, JWT token lifecycle, token expiration, tamper rejection, register & login API. | `PASSED` |
| **`test_parsers.py`** | 6 | WhatsApp multiline & iOS/Android formats, Call CSV/JSON, SMS CSV, EML MIME email, Chrome SQLite history, PDF/Text documents. | `PASSED` |
| **`test_storage_service.py`** | 2 | Chunked file streaming, real-time SHA-256 hash generation, filename sanitization. | `PASSED` |
| **`test_ingestion_pipeline.py`** | 1 | Automatic content-sniffing and parser dispatcher routing. | `PASSED` |
| **`test_pipelines.py`** | 4 | Normalization pipeline, multi-type Entity Extraction, Relationship Discovery, chronological Timeline ordering. | `PASSED` |
| **`test_embeddings_and_search.py`** | 2 | 384-dim vector generation, case-isolated semantic similarity search (Invariant 6). | `PASSED` |
| **`test_investigation_and_reports.py`** | 4 | Context Builder formatting, Investigation Agent citations, insufficient evidence handling, Report Agent synthesis. | `PASSED` |
| **`test_logging.py`** | 2 | Evidence masking filter, redacting phone numbers, emails, and crypto addresses from log records. | `PASSED` |
| **`test_evidence_api.py`** | 2 | Multipart evidence upload, artifact creation, invalid case error handling. | `PASSED` |
| **`test_ai_routes.py`** | 1 | End-to-end integration across `/api/search`, `/api/investigations`, and `/api/reports/generate`. | `PASSED` |
| **`test_end_to_end_forensics.py`** | 1 | Full-spectrum forensic lifecycle: Register -> Case -> Multi-evidence upload -> Entities & Graph -> Timeline -> Semantic Search -> Investigation Agent -> Report generation -> Cross-case isolation. | `PASSED` |
| **Total Test Suite** | **30** | **Comprehensive Full-Stack Coverage** | **`100% PASS`** |

---

## 10. License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
