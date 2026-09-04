# AI-CFO Reasoning & Reconciliation Agent — Implementation Plan (Frontend Rewrite)
**Track 04: AI Finance Controller — Razorpay Hackathon**

---

## 1. Executive Summary & Vision

We are replacing the temporary Streamlit/Swagger UI with a **standalone, production-grade React + TypeScript + Vite web application** styled with a **warm ivory, editorial fintech design system**.

The product architecture remains strictly decoupled:
- **Backend**: FastAPI REST service (`api.py`), deterministic finance tools (`tools.py`), provider-agnostic reasoning agent (`agent.py`), JSONL audit logging (`audit.py`), and usage metering (`usage.py`).
- **Frontend**: React + TypeScript + Vite single-page application (`frontend/`) communicating strictly via HTTP. All financial figures come from the backend.

---

## 2. Architecture & Data Flow

```text
                 FRONTEND (React + TS + Vite)
      Overview | Reconciliation | Review Queue | Ask AI | Audit | Usage
                               │
                               │ HTTP (VITE_API_BASE_URL)
                               ▼
                        FastAPI Backend
                               │
          ┌────────────────────┴────────────────────┐
          ▼                                         ▼
    AI Reasoning Agent                        Finance Tools
   (Anti-Hallucination)                  (Deterministic Calculations)
          │                                         │
          └────────────────────┬────────────────────┘
                               ▼
                       Existing CSV Data
```

---

## 3. Visual & Aesthetic Guidelines

- **Palette**: Warm ivory / off-white background (`#FAF9F5`), soft cream cards (`#FFFFFF` / `#F5F3ED`), soft charcoal typography (`#1E2022`), muted slate text (`#5E646E`), subtle warm gray borders (`#E6E3DB`), restrained slate-navy accent (`#1E3A8A`).
- **Feel**: Calm, editorial, trustworthy, human-crafted, finance-focused.
- **Anti-Clichés**: Zero purple AI gradients, zero glowing neon text, zero robot graphics, zero dark mode sci-fi dashboard gimmicks.

---

## 4. Frontend Modules to Create (`frontend/`)

1. **API Client & Type Definitions (`src/api/`)**:
   - `types.ts`: Strongly typed interfaces for BatchSummary, Transaction, Exception, LowConfidenceMatch, AuditEntry, UsageStats, AskResponse.
   - `client.ts`: Fetch-based HTTP client handling base URL, error states, and timeouts.
   - `reconciliation.ts`, `agent.ts`, `audit.ts`, `usage.ts`: Clean endpoint abstractions.

2. **Components & Layout (`src/components/`)**:
   - `AppLayout.tsx`, `Header.tsx`, `Sidebar.tsx`: Modern application shell with active status badges.
   - `ConfidenceBadge.tsx`, `StatusBadge.tsx`: Restrained visual indicators for match statuses and confidence.
   - `SkeletonLoader.tsx`: Calm skeleton loading states for AI reasoning.
   - `TransactionDrawer.tsx`: Slide-over detail panel for individual invoices with "Ask AI" trigger.

3. **Pages (`src/pages/`)**:
   - `OverviewPage.tsx`: 3-second comprehension header (80% match, 12 exceptions, 3 orphans, ₹1.09M exposure), category breakdown, low-confidence callout.
   - `ReconciliationPage.tsx`: Full dataset table with search, category filter, status filter, and pagination.
   - `ReviewQueuePage.tsx`: Dedicated view for borderline matches (3.0%–4.0% fee deduction near 3.5% threshold) with one-click AI review.
   - `AskAiPage.tsx`: Analyst investigation workspace with suggested questions, structured answer cards (Executive Finding, Evidence Table, Confidence Badge, Source), and expandable audit traces.
   - `AuditPage.tsx`: Immutable reverse-chronological audit log with secret scrubbing and tool call inspection.
   - `UsagePage.tsx`: API metering dashboard displaying total calls, tool breakdown, and compute units.

---

## 5. Verification Plan

1. Backend tests: `python test_agent.py` and `python eval_questions.py` continue to pass 100%.
2. Frontend build: `npm run build` succeeds without TypeScript or bundling errors.
3. User flow testing: End-to-end verification of Overview KPIs, Reconciliation filtering, Low-Confidence review, Ask AI investigation, Audit trail inspection, and Usage stats.
