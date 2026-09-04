"""
FastAPI REST API Service for Razorpay AI Finance Controller.
Provides API-first access to the AI-CFO reasoning layer, deterministic tools,
usage metering, and compliance audit trail.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from agent import ask
import tools
import usage
import audit

app = FastAPI(
    title="AI-CFO Reasoning Layer API",
    description="API-first AI finance operations reasoning engine for Razorpay Hackathon Track 04",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str = Field(..., description="Natural language finance question or transaction lookup")

class AskResponse(BaseModel):
    answer: str
    confidence: str
    evidence: List[Dict[str, Any]]
    tools_called: List[Dict[str, Any]]
    usage: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None

@app.get("/health", tags=["System"])
def health_check():
    """Operational health check endpoint."""
    return {"status": "OPERATIONAL", "service": "AI-CFO Reasoning Layer", "version": "1.0.0"}

@app.post("/ask", response_model=AskResponse, tags=["Reasoning"])
def ask_question(req: AskRequest):
    """
    Primary AI-CFO reasoning endpoint.
    Accepts natural language questions, coordinates tool execution, and returns
    evidence-backed explanations with confidence scoring.
    """
    res = ask(req.question)
    return res

@app.get("/usage", tags=["Metering"])
def get_usage():
    """Retrieve current session usage metering and PoC billing statistics."""
    return usage.get_usage_stats()

@app.get("/summary", tags=["Finance Tools"])
@app.get("/batch-summary", tags=["Finance Tools"])
def get_summary():
    """Retrieve deterministic batch reconciliation metrics."""
    return tools.get_batch_summary()

@app.get("/reconciliation", tags=["Finance Tools"])
def get_reconciliation():
    """Retrieve all reconciliation records."""
    return tools.get_all_reconciliation_records()

@app.get("/transactions/{identifier}", tags=["Finance Tools"])
def get_transaction_detail(identifier: str):
    """Retrieve detail of a single transaction or invoice."""
    return tools.get_transaction(identifier)

@app.get("/exceptions", tags=["Finance Tools"])
def get_exceptions(category: Optional[str] = Query(None, description="Optional category filter")):
    """List all reconciliation exceptions with optional category filtering."""
    return tools.list_exceptions(category=category)

@app.get("/review-queue", tags=["Finance Tools"])
@app.get("/low-confidence", tags=["Finance Tools"])
def get_review_queue():
    """List low-confidence matches flagged for human review near tolerance boundary."""
    return tools.get_low_confidence_matches()

@app.get("/audit", tags=["Audit & Governance"])
def get_audit(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    """Retrieve immutable chronological audit trail."""
    return audit.get_audit_trail(limit=limit, offset=offset)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

