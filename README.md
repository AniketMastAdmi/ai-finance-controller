# AI-CFO Reasoning & Reconciliation Layer
### **Track 04: AI Finance Controller — Razorpay Hackathon**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%203.7%20Flash-4285F4.svg)](https://deepmind.google/technologies/gemini/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg)](https://vitejs.dev/)
[![Evaluation Accuracy](https://img.shields.io/badge/Eval%20Accuracy-100%25-brightgreen.svg)]()
[![Zero Hallucinations](https://img.shields.io/badge/Hallucination%20Violations-0-success.svg)]()

> **"The reconciliation engine tells you what happened. The AI-CFO explains why, flags borderline reconciliation decisions, normalizes gateway feeds, and provides verifiable evidence for every action."**

---

## 1. Product Overview & Core Thesis

Traditional reconciliation engines are deterministic matching systems that categorize transactions into basic statuses (`MATCHED`, `EXCEPTION`). However, finance controllers face three major operational bottlenecks:
1. **Explainability Void**: When an invoice fails matching, finance analysts spend hours manually cross-referencing ledger tables and gateway logs to understand *why*.
2. **Tolerance Blind Spots**: Static tolerance bands (e.g. 1.0%–3.5% gateway fee deduction) automatically mark borderline transactions as `MATCHED`, potentially concealing unauthorized discounts, incorrect fee tiers, or pending disputes.
3. **Audit & Compliance Risk**: Generic AI chatbots hallucinate figures and offer zero audit trails for SOX/SOC2 compliance.

The **AI-CFO Reasoning Layer** sits on top of existing financial infrastructure to provide an **API-first, auditable intelligence layer** that reasons over deterministic tool outputs, computes confidence scores, and maintains an immutable audit trail.

---

## 2. System Architecture

```text
               FRONTEND (React 18 + TypeScript + Vite)
 Overview | Reconciliation | Review Queue | Ask AI | Audit | Usage & Metering | SMB Partner Portal
                                │
                                │ HTTP / REST (VITE_API_BASE_URL)
                                ▼
                     FastAPI Backend (api.py)
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
  Google Gemini Core      Finance Tools         Razorpay Adapter
(gemini-3.7-flash Multi- (Deterministic Math   (External Settlement
 Turn Function Calling)    & Data Integrity)       Normalizer)
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                        Existing CSV Data
          invoices.csv (60 Invoices) | settlements.csv (63 Txns)
```

### Key Architectural Tenets:
- **No Uncontrolled Arithmetic**: The LLM is strictly prohibited from doing mental math. Aggregations, percentages, and variance calculations are executed exclusively by deterministic Python finance tools.
- **Google Gemini Function Calling**: Powered by `gemini-3.7-flash` using native tool declarations (`GEMINI_TOOLS_DECLARATION`) and multi-turn function call loops.
- **Fail-Safe Confidence Precedence**: Machine-verifiable criteria enforce deterministic confidence (`HIGH_CONFIDENCE`, `LOW_CONFIDENCE`, `UNRESOLVED`) regardless of LLM verbal sentiment.
- **Gateway Adapter Layer**: Normalized schema adapter (`adapter.py`) ingests raw Razorpay settlement webhooks and converts them into canonical reconciliation formats.

---

## 3. Core Deterministic Finance Tools & Endpoints

All calculations are executed deterministically in `tools.py` and `adapter.py`:

| Tool / Module | Function Signature | Description |
|---|---|---|
| **Tool 1** | `get_transaction(identifier)` | Fetches complete financial lifecycle by Invoice ID or Settlement ID; returns status, fee variance, and confidence flags. |
| **Tool 2** | `list_exceptions(category=None)` | Returns all 12 invoice-level exceptions with optional filtering (`amount_mismatch`, `timing_gap`, `missing_settlement`, `duplicate_settlement`, `orphan_settlement`). |
| **Tool 3** | `get_batch_summary()` | Computes batch KPIs: 80% match rate, ₹1,093,000 exception exposure, ₹210,500 orphan settlement value. |
| **Tool 4** | `get_low_confidence_matches()` | Identifies `MATCHED` fee deductions sitting within 0.5% of the 3.5% upper boundary (`3.0% <= % <= 4.0%`). |
| **Tool 5** | `get_all_reconciliation_records()` | Retrieves all 60 ledger reconciliation records from `reconciliation_report.csv`. |
| **Adapter** | `RazorpaySettlementAdapter.normalize_record()` | Normalizes raw Razorpay settlement payloads (amounts in paise, fee breakdowns, UTRs) to canonical engine schema. |

---

## 4. Known Reconciliation Limitation & Low-Confidence Detection

The reconciliation engine uses a standard gateway fee tolerance band of **1.0% to 3.5%**. 

Transactions with fee deductions near the upper boundary (e.g. `INV1046` at 3.20%, `INV1047` at 3.40%, and `INV1048` at 3.45%) are marked `MATCHED` by the baseline engine. The AI-CFO layer detects these borderline transactions using `get_low_confidence_matches()`, labels them as `LOW_CONFIDENCE`, and generates a **Review Recommended** finding so finance teams can manually review whether the deduction represents a legitimate gateway fee or an unauthorized discount.

---

## 5. Frontend Architecture & Design System

The application features a modern, standalone web application located in `frontend/` styled with a **warm ivory, editorial fintech aesthetic**:

* **Color Palette**:
  - Background: Warm off-white / ivory (`#FAF9F5`)
  - Cards & Panels: Soft cream surfaces (`#FFFFFF`, `#F6F4EE`) with subtle warm borders (`#E8E5DC`)
  - Typography: Soft charcoal (`#1E2022`) using Inter and JetBrains Mono
  - Accent: Restrained slate-navy (`#1E3A8A`) and muted status indicators
  - Anti-Clichés: Zero purple AI gradients, zero glowing robot graphics, zero dark mode sci-fi templates
* **7 Core Pages**:
  1. **Overview**: 3-second comprehension header (80% match, 12 exceptions, 3 orphans, ₹1.09M exposure), category breakdown, and low-confidence callout.
  2. **Reconciliation Ledger**: 60-invoice table with search, category & status filters, pagination, and a slide-over detail drawer with an **"Ask AI-CFO"** trigger.
  3. **Review Queue**: Dedicated borderline match review (3.0%–4.0% fee deduction near 3.5% tolerance limit) with tolerance delta metrics.
  4. **Ask AI-CFO Workspace**: Analyst investigation workspace with suggested query chips, structured answer cards (Executive Finding, Verifiable Evidence Table, Confidence Badge, Source), and expandable audit traces.
  5. **Governance & Audit Trail**: Chronological, secret-scrubbed inspection log with tool calls, arguments, and latency measurements.
  6. **Operations & API Metering**: Real-time telemetry tracking session questions, tool distribution, compute units, and an **interactive commercial pricing tier simulator** ($0.05, $0.10, $0.15 USD with live INR conversion).
  7. **SMB Partner Portal Embed Demo**: Demonstrates external embeddability of Razorpay AI-CFO reasoning into third-party merchant SaaS / ERP dashboards.

---

## 6. Getting Started & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (tested with v22) & npm

### Step 1: Set Up Backend Virtual Environment
```powershell
# 1. Navigate to project root
cd "d:\Razorpay\AI Finance controller"

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Copy .env.example to .env and set your GEMINI_API_KEY
cp .env.example .env
```

### Step 2: Install Frontend Dependencies
```powershell
# In the frontend directory:
cd "d:\Razorpay\AI Finance controller\frontend"
npm install
```

---

## 7. Running the Applications

### 1. Launch FastAPI REST Service (Backend)
```powershell
# In project root (with venv activated):
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
*API running at: `http://localhost:8000` (Interactive Swagger docs at `http://localhost:8000/docs`)*

### 2. Launch Modern React + TypeScript Web App (Primary User Interface)
```powershell
# In the frontend directory:
cd "d:\Razorpay\AI Finance controller\frontend"
npm run dev
```
*Access the AI-CFO application at: **`http://localhost:5173`***

### 3. Programmatic Usage (Decoupled Core)
```python
from agent import ask

result = ask("Why didn't INV1060 match?")
print(result["answer"])
print("Confidence:", result["confidence"])
print("Evidence:", result["evidence"])
```

---

## 8. API Reference

### `POST /ask`
Submit natural language finance questions.
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Why didn'\''t INV1060 match?"}'
```

**Response**:
```json
{
  "answer": "Invoice INV1060 for Pinnacle Foods (₹145,000.00) triggered a DUPLICATE_SETTLEMENT exception. Multiple settlements (SET1059; SET1060) were received totaling ₹290,000.00...",
  "confidence": "HIGH_CONFIDENCE",
  "evidence": [
    {
      "invoice_id": "INV1060",
      "transaction_id": "SET1059; SET1060",
      "customer": "Pinnacle Foods",
      "invoice_amount": 145000.0,
      "settlement_amount": 290000.0,
      "status": "EXCEPTION",
      "reason": "duplicate_settlement",
      "source": "reconciliation_report.csv"
    }
  ],
  "tools_called": [
    {
      "name": "get_transaction",
      "arguments": {"identifier": "INV1060"},
      "latency_ms": 1.2
    }
  ],
  "usage": {
    "calls_this_session": 1,
    "total_tool_calls": 1,
    "calls_by_tool": {"get_transaction": 1}
  },
  "error": null
}
```

### Commercial & Integration Endpoints
- `POST /usage/pricing`: Dynamically configure investigation tier (`{"tier_usd": 0.10}`).
- `POST /adapter/normalize-settlements`: Ingest and standardize raw Razorpay gateway settlement feeds.
- `GET /summary` (or `/batch-summary`): Returns batch reconciliation KPIs.
- `GET /reconciliation`: Returns all 60 reconciliation ledger records.
- `GET /transactions/{identifier}`: Single transaction detail lookup.
- `GET /exceptions`: Returns filterable exception list.
- `GET /review-queue` (or `/low-confidence`): Returns low-confidence borderline matches.
- `GET /usage`: Returns usage metering and estimated cost statistics.
- `GET /audit`: Returns secret-scrubbed audit trail.

---

## 9. Verification & Evaluation Results

### Run Unit Test Suite (17 Tests)
```bash
python test_agent.py
```
**Results**:
- `17/17 tests passed (100.0%)`
- Verifies: pinned metrics (80% match, 12 exceptions, 3 orphans), Razorpay settlement adapter, missing `GEMINI_API_KEY` handling, Gemini tool-calling loop, audit log scrubbing, and dynamic pricing calculations.

### Run Held-Out Evaluation Suite (10 Multi-Phrased Questions)
```bash
python eval_questions.py
```

**Benchmark Results**:
```text
=================================================================
Agent Evaluation Summary
─────────────────────────
Questions Tested:         10
Passed:                   10
Failed:                   0
Accuracy:                 100.0%

Tool Selection Accuracy:  100.0%
Failure Handling Rate:    100.0%
Hallucination Violations: 0
=================================================================
```

### Build Frontend Production Assets
```powershell
cd frontend
npm run build
```
**Results**:
- `✓ built in 19.52s with 0 TypeScript errors`

---

## 10. Governance, Auditability & Commercial Roadmap

- **Immutable Audit Log (`audit_log.jsonl`)**: Every user interaction, tool invocation, argument, response, and confidence score is appended to `audit_log.jsonl`.
- **Automated Secret Scrubbing**: All API keys, tokens, and authorization headers are scrubbed before logging.
- **Pay-Per-Investigation API Monetization**: Configurable tiers ($0.05 Starter, $0.10 Standard, $0.15 Enterprise) with real-time USD/INR cost conversion to support B2B SaaS integrations.
- **Target Integrations**:
  - Payment Gateways (Razorpay, Stripe, Adyen)
  - ERP & Accounting Platforms (SAP, Oracle NetSuite, Tally, QuickBooks)
  - Treasury Management Systems (TMS)
