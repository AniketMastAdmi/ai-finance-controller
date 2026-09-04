# AI-CFO Reasoning & Reconciliation Layer — Judge Demo Script
**Track 04: AI Finance Controller — Razorpay Hackathon**
**Time: 3–5 Minutes**

---

## Demo Overview & Positioning

> **"The reconciliation engine tells you what happened. The AI-CFO explains why, flags borderline reconciliation decisions, and provides verifiable evidence for every action."**

This prototype is an **API-first financial operations reasoning layer** paired with a **production-grade React + TypeScript web application**. It features an editorial, warm-ivory fintech design system—rejecting generic AI chat bubbles and dark neon templates in favor of a serious finance operations workspace.

---

## Step-by-Step Presentation Script

### Step 1: Open Application (3-Second Health Comprehension)
* **Action**: Open the React web application at **`http://localhost:5173`** (Overview page).
* **Point out the Visual Design**:
  - Warm ivory / off-white background (`#FAF9F5`), soft charcoal typography, subtle warm gray borders.
  - Calm, trustworthy, editorial fintech look and feel.
* **Judge Sees Immediately**:
  - **Match Rate**: `80.0%` (48 / 60 invoices matched)
  - **Invoice Exceptions**: `12` (20.0% exception rate)
  - **Exception Exposure**: `₹1,093,000` (Capital at risk)
  - **Orphan Settlements**: `3` (`₹210,500` unlinked funds in gateway)
  - **Exception Breakdown**: Amount Mismatch (3), Timing Gap (3), Missing Settlement (3), Duplicate Settlement (3).
* **Script**:
  > *"Welcome judges. In finance operations, speed and trust are everything. Within 3 seconds on our Overview dashboard, a finance controller sees the full batch health: an 80% match rate, 12 exceptions across 4 distinct failure categories, and 3 orphan settlements representing ₹2.1L in unlinked gateway receipts."*

---

### Step 2: The Review Queue & Engine Blind Spots
* **Action**: In the sidebar, click on **`Review Queue`** (highlight the amber notification badge `3`).
* **Judge Sees**:
  - Invoices like `INV1046` (3.20% deduction), `INV1047` (3.40% deduction), and `INV1048` (3.45% deduction).
  - Status: `LOW CONFIDENCE • REVIEW RECOMMENDED`.
  - Boundary distance metrics (e.g. `0.05%` from the `3.50%` upper tolerance limit).
* **Script**:
  > *"Here is one of our key product innovations. Traditional reconciliation engines use static tolerance bands—here, 1.0% to 3.5% fee deduction. A transaction with a 3.45% deduction is classified as MATCHED by the engine, but in reality, it could be a concealed price dispute or unauthorized short payment. Our AI-CFO confidence layer identifies these borderline matches and flags them for controller review before books are closed."*

---

### Step 3: Interactive Reconciliation Ledger & Slide-Over Drawer
* **Action**: Navigate to **`Reconciliation`** in the sidebar. Filter by category `duplicate_settlement` or type `INV1060` in the search bar. Click the row for `INV1060`.
* **Judge Sees**:
  - Slide-over `TransactionDrawer` opens from the right.
  - Complete financial breakdown: Customer (Atlas Mobility), Invoice Amount (₹145,000), Settled Amount (₹290,000), Multiple Settlement IDs (`SET1059; SET1060`), Status (`EXCEPTION • duplicate_settlement`).
  - Prominent action button: **`Ask AI-CFO About This Transaction`**.
* **Action**: Click **`Ask AI-CFO About This Transaction`**.
* **Script**:
  > *"Finance teams need smooth workflows. In our Reconciliation Ledger, clicking any transaction opens a slide-over inspection drawer. Clicking 'Ask AI-CFO' hands off the transaction directly to our reasoning core."*

---

### Step 4: AI Investigation & Machine-Readable Evidence
* **Action**: The app smoothly transitions to the **`Ask AI-CFO`** workspace with the question pre-filled and running.
* **Judge Sees**:
  - Calm skeleton loader while the reasoning engine executes tools.
  - **Executive Finding**: 
    > `Invoice INV1060 for Atlas Mobility (₹145,000.00) triggered a DUPLICATE_SETTLEMENT exception. Multiple settlements (SET1059; SET1060) were received totaling ₹290,000.00. This indicates a potential double disbursement or split settlement requiring immediate review.`
  - **Confidence Badge**: `HIGH CONFIDENCE` (Muted emerald badge).
  - **Verifiable Financial Evidence Table**: Machine-readable breakdown listing invoice ID, transaction IDs, customer, amounts, status, and source file (`reconciliation_report.csv`).
  - **Expandable Audit Trace**: Click `▸ View Audit Trail & Tool Calls` to show deterministic tool `get_transaction`, arguments `{"identifier": "INV1060"}`, latency `1.2ms`, and raw JSON output.
* **Script**:
  > *"The AI doesn't guess or hallucinate numbers. It calls our deterministic `get_transaction` tool, detects the duplicate disbursement of ₹2.9L across two settlement records, and generates an executive summary backed by verifiable machine evidence and an inspection trace."*

---

### Step 5: Ask a Batch-Level Financial Exposure Question
* **Action**: In the `Ask AI-CFO` input, click the suggested chip: **`What's my total exception exposure in this batch?`**
* **Judge Sees**:
  - Exact calculated exposure: `₹1,093,000.00` across 12 exceptions plus `₹210,500.00` across 3 orphan settlements.
  - Tool executed: `get_batch_summary`.
* **Script**:
  > *"The AI-CFO does not perform token arithmetic. It delegates mathematical aggregations to `get_batch_summary`, guaranteeing zero numerical drift."*

---

### Step 6: Anti-Hallucination & Graceful Failure Handling
* **Action**: In the question box, click the chip: **`Why didn't INV9999 match?`**
* **Judge Sees**:
  - **Executive Finding**: `Transaction / Invoice 'INV9999' was not found in the reconciliation dataset. No matching invoice or settlement record exists in the system.`
  - **Confidence Badge**: `UNRESOLVED` (Muted red badge).
  - No fabricated customer names, no made-up amounts.
* **Script**:
  > *"When queried on nonexistent invoice INV9999, the AI refuses to fabricate data. It returns an UNRESOLVED status with a clear failure explanation—preventing financial hallucinations."*

---

### Step 7: Immutable Governance & Audit Trail
* **Action**: Click on **`Audit Trail`** in the sidebar.
* **Judge Sees**:
  - Chronological list of every interaction logged to `audit_log.jsonl`.
  - Expand any row to show timestamps, scrubbed arguments, latency, confidence, and tools executed.
* **Script**:
  > *"Every single query, tool execution, argument, and answer is permanently logged in an append-only JSONL audit log with automated secret scrubbing for SOX/SOC2 compliance."*

---

### Step 8: API Metering & Commercial Readiness
* **Action**: Click on **`API Metering`** in the sidebar.
* **Judge Sees**:
  - Live session telemetry: Questions Answered, Total Tool Calls, Avg Tools/Question, and Compute Units.
  - Deterministic Tool Invocations breakdown table: `get_transaction`, `list_exceptions`, `get_batch_summary`, `get_low_confidence_matches`.
* **Script**:
  > *"Finally, the system is commercially architected for API monetization. We meter every tool and investigation, ready for a pay-per-operation pricing model across banking, ERP, and payment gateway integrations."*

---

## Conclusion & Judge Takeaway
> **"We didn't build an AI chatbot with financial data attached. We built a production-grade finance operations reasoning engine that turns raw reconciliation results into verified, auditable business decisions."**
