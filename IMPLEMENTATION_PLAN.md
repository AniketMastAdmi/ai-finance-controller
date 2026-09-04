# AI-CFO Reasoning Layer — Gemini Migration & Extensions Implementation Plan
**Track 04: AI Finance Controller — Razorpay Hackathon**

---

## 1. Executive Summary & Vision

This phase replaces all keyword/semantic routing and Anthropic/Claude references with a **genuine Google Gemini tool-calling engine** using the Google Gemini ecosystem.

Key objectives:
- **Zero fake AI**: Real LLM tool/function calling (`gemini-3.7-flash`).
- **Controlled execution**: Approved tool registry executing only existing deterministic finance tools from `tools.py`.
- **Grounded reasoning**: Machine evidence extraction, anti-hallucination guardrails, and deterministic confidence precedence.
- **Razorpay Settlement Adapter**: Normalization layer for real-world payment gateway settlements.
- **Estimated Usage Cost Demo**: Configurable pricing tiers ($0.05, $0.10, $0.15) with USD & INR conversion.
- **Mock Partner SMB Embed**: Standalone SMB merchant dashboard ("Acme Merchant Portal") proving plug-and-play API embeddability.

---

## 2. Architecture & Data Flow

```text
                 React + TypeScript / Partner SMB Portal
                               │
                               ▼
                          FastAPI API
                               │
                               ▼
                         AI-CFO Agent
                               │
                               ▼
                   Google Gemini (gemini-3.7-flash)
                    Tools: function_declarations
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
       Deterministic Tools                 Audit Logger
     (Controlled Registry)              (audit_log.jsonl)
              │
              ▼
    CSV Reconciliation Data
```

---

## 3. Configuration & Missing Key Error Handling

If `GEMINI_API_KEY` is not set, the agent responds with a clear configuration error:
```text
GEMINI_API_KEY is not configured.
Please configure your Gemini API key before using the AI reasoning service.
```
No keyword-routing fallback or fabricated answers.

---

## 4. Verification & Testing

- `test_agent.py`: Pinned deterministic assertions pass without requiring a live Gemini API key.
- `eval_questions.py`: 10 held-out questions with natural language variations tested against Gemini function calling.
- Frontend: Verified build and interactive pricing & partner embed demonstration.
