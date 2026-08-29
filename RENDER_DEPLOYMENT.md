# 🚀 Deploying TraceLens on Render: Complete Guide

This guide provides step-by-step instructions to deploy the entire **TraceLens Digital Forensics Intelligence Platform** on [Render](https://render.com).

---

## 🏗️ Architecture Overview

TraceLens on Render consists of three decoupled, high-performance components:

```
┌────────────────────────────────────────────────────────┐
│  Render Static Site: tracelens-frontend                │
│  - React 19 + Vite 8 + Tailwind CSS v4                 │
│  - Global CDN, fast asset caching                      │
│  - Automatic SPA rewrites via _redirects               │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS (REST API + JWT)
                           ▼
┌────────────────────────────────────────────────────────┐
│  Render Web Service: tracelens-backend                 │
│  - FastAPI ASGI Server (python run.py)                 │
│  - Forensic Parsers & Multi-Type Entity Extraction     │
│  - Safe Centralized Logging & Evidence Redaction       │
└────────────┬─────────────────────────────┬─────────────┘
             │ SQL + pgvector              │ Chunked I/O
             ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│ Render PostgreSQL       │   │ Ephemeral / Mounted Disk │
│ - pgvector (384-dim)    │   │ - storage/evidence/      │
│ - Invariant 6 Isolation │   │ - SHA-256 Checksums      │
└─────────────────────────┘   └──────────────────────────┘
```

---

## ⚡ Method 1: 1-Click Render Blueprint (Recommended)

TraceLens includes a native [`render.yaml`](./render.yaml) blueprint specification that automatically creates and interconnects the PostgreSQL database, FastAPI backend, and React frontend with zero manual configuration.

### Steps:

1. **Push your code to GitHub**:
   Ensure all changes are committed and pushed to your GitHub repository:
   ```bash
   git add .
   git commit -m "Configure Render deployment blueprints and database connection"
   git push origin main
   ```

2. **Open Render Dashboard**:
   - Navigate to [dashboard.render.com](https://dashboard.render.com).
   - Click the **"New +"** button in the top navigation bar.
   - Select **"Blueprint"**.

3. **Connect Repository**:
   - Select your `TraceLens` GitHub repository.
   - Render will parse `render.yaml` and display the blueprint plan:
     - 🗄️ **`tracelens-db`** (PostgreSQL 16)
     - ⚙️ **`tracelens-backend`** (Web Service)
     - 🌐 **`tracelens-frontend`** (Static Site)

4. **Review & Deploy**:
   - Click **"Apply"**.
   - Render will provision the database first, inject `DATABASE_URL` into the backend, and inject the backend URL into `VITE_API_URL` for the frontend.
   - Wait 2–3 minutes for builds to complete.

---

## 🛠️ Method 2: Manual Dashboard Setup

If you prefer to configure each service manually in the Render dashboard:

### Step 1: Provision Managed PostgreSQL (`tracelens-db`)

1. Click **"New +"** -> **"PostgreSQL"**.
2. Configure database settings:
   - **Name**: `tracelens-db`
   - **Database**: `tracelens`
   - **User**: `tracelens`
   - **Region**: Choose closest to you (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **PostgreSQL Version**: `16` (or `15`)
   - **Plan**: `Free`
3. Click **"Create Database"**.
4. Once created, copy the **Internal Database URL** (for services in same region) or **External Database URL**.

---

### Step 2: Deploy Backend Web Service (`tracelens-backend`)

1. Click **"New +"** -> **"Web Service"**.
2. Select your `TraceLens` repository.
3. Configure the service settings:
   - **Name**: `tracelens-backend`
   - **Region**: *Same region as your database*
   - **Branch**: `main`
   - **Root Directory**: `Server`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     python run.py
     ```
   - **Plan**: `Free`
4. Expand **"Advanced"** and add the following **Environment Variables**:

   | Key | Value / Source | Notes |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Ensures Python 3.11 runtime |
   | `DATABASE_URL` | *Paste from Step 1* (or choose "Add Environment Variable from other service") | Auto-converts `postgres://` to `postgresql+psycopg2://` |
   | `SECRET_KEY` | *(Generate a random 32+ character string)* | Used for cryptographic JWT signing |
   | `ALLOWED_ORIGINS` | `*` *(or your frontend URL)* | CORS access list |
   | `STORAGE_PATH` | `./storage/evidence` | Evidence upload location |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24-hour investigator session |
   | `GEMINI_API_KEY` *(Optional)* | `AIza...` | For Gemini 2.5 Flash LLM reasoning |
   | `OPENAI_API_KEY` *(Optional)* | `sk-...` | For OpenAI LLM reasoning |

5. Under **"Health Check Path"**, set:
   ```
   /health
   ```
6. Click **"Create Web Service"**.
7. Once deployed, note your backend public URL (e.g. `https://tracelens-backend.onrender.com`).

---

### Step 3: Deploy Frontend Static Site (`tracelens-frontend`)

1. Click **"New +"** -> **"Static Site"**.
2. Select your `TraceLens` repository.
3. Configure static site settings:
   - **Name**: `tracelens-frontend`
   - **Branch**: `main`
   - **Root Directory**: `Client`
   - **Build Command**:
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**:
     ```bash
     dist
     ```
4. Under **"Environment Variables"**, add:

   | Key | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://tracelens-backend.onrender.com/api` |

   *(Note: The client auto-appends `/api` if you only enter `https://tracelens-backend.onrender.com`)*

5. Under **"Redirects / Rewrites"**:
   *(TraceLens already includes `Client/public/_redirects` which handles this automatically; you can also configure it in the UI):*
   - **Type**: `Rewrite`
   - **Source**: `/*`
   - **Destination**: `/index.html`

6. Click **"Create Static Site"**.
7. Your app is live at `https://tracelens-frontend.onrender.com`!

---

## 🔍 Verification & Health Check

### 1. Verify Backend & pgvector
Navigate to your backend URL in your browser:
- `https://<your-backend-url>/health`

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "postgresql"
}
```

### 2. Verify Swagger / Interactive API Docs
Visit:
- `https://<your-backend-url>/docs`

### 3. Verify Frontend Ingestion & Graph
1. Open `https://<your-frontend-url>`.
2. Register a new investigator account.
3. Create a Case (e.g. "Case ALPHA-2026").
4. Upload sample evidence (`.txt` WhatsApp chat, `.csv` CDR logs, or `.eml` email).
5. Verify timeline reconstruction, entity extraction, and ReactFlow graph visualization.

---

## 💡 Operational & Production Tips

### A. Free Tier Cold Starts
On Render's free tier, Web Services spin down after 15 minutes of inactivity. When a request arrives, the service takes ~30–50 seconds to spin back up.
- **Remedy**: For zero-downtime production environments, upgrade the Web Service to Render's **Starter** tier ($7/month) to keep it always active.

### B. Persistent Evidence Disk (Optional)
On free web services, the local file storage (`./storage/evidence`) is ephemeral (resets on service rebuild).
- If you need uploaded files to persist across service redeploys on Render, attach a **Persistent Disk** (Render Dashboard -> Service -> Disks) mounted at `/var/data` and set:
  ```env
  STORAGE_PATH=/var/data/evidence
  ```
- Note that all parsed forensic artifacts, timelines, entities, and vector embeddings are stored in the **PostgreSQL database**, which is already persistent!

### C. Offline Fallback & LLM Keys
TraceLens works immediately without any external AI API keys. If `GEMINI_API_KEY` or `OPENAI_API_KEY` is not provided:
- Vector embeddings use deterministic unit-normalized 384-dimensional fallback vectors.
- The AI Investigation Agent uses the deterministic rule-based evidentiary reasoning engine adhering to all AGENT.md invariants.
