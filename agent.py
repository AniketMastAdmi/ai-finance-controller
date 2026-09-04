"""
AI-CFO Reasoning Core for Razorpay AI Finance Controller.
Powered by Google Gemini with native tool/function calling.

The reasoning agent executes:
Natural-language question -> Gemini decides tool -> Controlled execution of tools.py -> 
Evidence returned -> Gemini explains result -> Deterministic confidence enforcement -> Audit log.

Directly importable:
    from agent import ask
    result = ask("Why didn't INV1060 match?")
"""

import time
import requests
from typing import Dict, Any, List, Optional
import tools
import audit
import usage
from config import GEMINI_MODEL, GEMINI_API_KEY, LOW_CONFIDENCE_LOWER, LOW_CONFIDENCE_UPPER

SYSTEM_PROMPT = """You are the AI-CFO Finance Controller Reasoning Layer.
Your role is to explain reconciliation results, identify low-confidence borderline matches, and provide verified evidence for finance operations teams.

Strict Operational Guidelines:
1. Never invent or hallucinate an invoice ID, transaction ID, customer, amount, settlement date, or financial metric.
2. Every answer must be supported by evidence retrieved from deterministic tools.
3. If a transaction is not found, state plainly that it does not exist in the reconciliation records.
4. If a transaction is classified as MATCHED but has a fee deduction near the upper tolerance limit (3.0% - 4.0%), state clearly that the reconciliation engine classified it as MATCHED, but the AI-CFO confidence layer recommends human review because it is close to the fee tolerance boundary.
5. Clearly distinguish between facts (tool outputs) and interpretation (reconciliation assessment).
6. Do not perform independent financial arithmetic when a deterministic tool provides the calculation.
7. Always provide clear, professional, executive-grade financial explanations."""

# Approved Deterministic Tool Registry
TOOL_REGISTRY = {
    "get_transaction": tools.get_transaction,
    "list_exceptions": tools.list_exceptions,
    "get_batch_summary": tools.get_batch_summary,
    "get_low_confidence_matches": tools.get_low_confidence_matches,
    "get_all_reconciliation_records": tools.get_all_reconciliation_records,
}

# Google Gemini Function Declarations Schema
GEMINI_TOOLS_DECLARATION = [
    {
        "function_declarations": [
            {
                "name": "get_transaction",
                "description": "Retrieve complete financial details about a specific invoice or transaction (status, invoice amount, settlement amount, deduction percentage, days to settle, confidence).",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "identifier": {
                            "type": "STRING",
                            "description": "The invoice ID (e.g. INV1060, INV1001) or settlement/transaction ID (e.g. SET1060, RZP_PAY_xxx)."
                        }
                    },
                    "required": ["identifier"]
                }
            },
            {
                "name": "list_exceptions",
                "description": "List all invoice-level exceptions or filter by specific exception category.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "category": {
                            "type": "STRING",
                            "description": "Optional category filter: 'amount_mismatch', 'timing_gap', 'missing_settlement', 'duplicate_settlement', or 'orphan_settlement'."
                        }
                    }
                }
            },
            {
                "name": "get_batch_summary",
                "description": "Retrieve deterministic batch-level financial metrics (total invoices, match rate %, total exception count, total exception exposure in INR, orphan settlements count & INR value, category breakdown).",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            },
            {
                "name": "get_low_confidence_matches",
                "description": "Find transactions classified as MATCHED under fee deduction whose deduction percentage is borderline (within 0.5% of upper 3.5% boundary: 3.0% - 4.0%), requiring human review.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            },
            {
                "name": "get_all_reconciliation_records",
                "description": "Retrieve all 60 reconciliation ledger records from reconciliation_report.csv.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            }
        ]
    }
]


def _call_gemini_api(contents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute raw HTTP request to Google Gemini API with system instructions and tools."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": contents,
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "tools": GEMINI_TOOLS_DECLARATION,
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024
        }
    }
    
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
    
    if response.status_code != 200:
        error_msg = response.text
        try:
            err_json = response.json()
            error_msg = err_json.get("error", {}).get("message", response.text)
        except Exception:
            pass
        raise RuntimeError(f"Gemini API Error ({response.status_code}): {error_msg}")
        
    return response.json()


def _execute_tool_safely(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool strictly from the approved registry with latency tracking."""
    if tool_name not in TOOL_REGISTRY:
        return {
            "success": False,
            "data": None,
            "error": {
                "type": "UNKNOWN_TOOL",
                "message": f"Tool '{tool_name}' is not in the approved financial tools registry."
            }
        }
        
    tool_func = TOOL_REGISTRY[tool_name]
    t0 = time.time()
    try:
        result = tool_func(**args)
    except Exception as e:
        result = {
            "success": False,
            "data": None,
            "error": {
                "type": "TOOL_EXECUTION_ERROR",
                "message": str(e)
            }
        }
    latency_ms = round((time.time() - t0) * 1000, 2)
    return {
        "name": tool_name,
        "arguments": args,
        "result": result,
        "latency_ms": latency_ms
    }


def _extract_evidence_and_confidence(tools_called: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
    """Extract machine-readable evidence items and apply deterministic confidence precedence."""
    evidence = []
    confidence = "HIGH_CONFIDENCE"
    
    for tc in tools_called:
        t_name = tc["name"]
        res = tc["result"]
        
        if not res.get("success", False):
            if res.get("error", {}).get("type") in ("TRANSACTION_NOT_FOUND", "INVALID_IDENTIFIER_FORMAT"):
                confidence = "UNRESOLVED"
            continue
            
        data = res.get("data")
        if not data:
            continue
            
        if t_name == "get_transaction":
            ev_item = {
                "invoice_id": data.get("invoice_id", "NONE"),
                "transaction_id": data.get("transaction_id", "NONE"),
                "customer": data.get("customer", "UNKNOWN"),
                "invoice_amount": data.get("invoice_amount", 0.0),
                "settlement_amount": data.get("settlement_amount", 0.0),
                "status": data.get("status"),
                "reason": data.get("reason"),
                "deduction_percentage": data.get("deduction_percentage", 0.0),
                "source": res.get("source", "reconciliation_report.csv")
            }
            evidence.append(ev_item)
            if data.get("confidence") == "LOW_CONFIDENCE":
                confidence = "LOW_CONFIDENCE"
                
        elif t_name == "get_low_confidence_matches":
            confidence = "LOW_CONFIDENCE"
            for m in data.get("matches", []):
                evidence.append({
                    "invoice_id": m.get("invoice_id"),
                    "transaction_id": m.get("transaction_id"),
                    "customer": m.get("customer"),
                    "invoice_amount": m.get("invoice_amount"),
                    "settled_amount": m.get("settled_amount"),
                    "deduction_percentage": m.get("deduction_percentage"),
                    "distance_from_boundary": m.get("distance_from_boundary"),
                    "source": res.get("source", "reconciliation_report.csv")
                })
                
        elif t_name == "list_exceptions":
            for exc in data.get("exceptions", []):
                evidence.append({
                    "invoice_id": exc.get("invoice_id", "NONE"),
                    "transaction_id": exc.get("transaction_id", "NONE"),
                    "customer": exc.get("customer"),
                    "amount": exc.get("invoice_amount") or exc.get("settlement_amount"),
                    "reason": exc.get("reason"),
                    "source": res.get("source", "reconciliation_report.csv")
                })
                
        elif t_name == "get_batch_summary":
            evidence.append({
                "total_invoices": data.get("total_invoices"),
                "match_rate": f"{data.get('match_rate_percentage')}%",
                "exception_invoices": data.get("exception_invoices"),
                "total_exception_exposure_inr": data.get("total_exception_exposure_inr"),
                "orphan_settlement_count": data.get("orphan_settlement_count"),
                "source": res.get("source", "reconciliation_report.csv")
            })
            
    return evidence, confidence


def ask(question: str) -> Dict[str, Any]:
    """
    Public entry point for AI-CFO reasoning layer.
    Coordinates genuine Google Gemini tool-calling, logs audit trails, meters usage,
    and returns structured response with answer, confidence, and machine evidence.
    """
    if not question or not isinstance(question, str) or not question.strip():
        usage.record_question_call(success=False)
        return {
            "answer": "Please provide a valid financial question or transaction identifier.",
            "confidence": "UNRESOLVED",
            "evidence": [],
            "tools_called": [],
            "usage": usage.get_usage_stats(),
            "error": {
                "type": "EMPTY_QUESTION",
                "message": "The query string was empty."
            }
        }
        
    # Check for GEMINI_API_KEY
    if not GEMINI_API_KEY:
        usage.record_question_call(success=False)
        error_info = {
            "type": "CONFIG_ERROR",
            "message": "GEMINI_API_KEY is not configured. Please configure your Gemini API key before using the AI reasoning service."
        }
        ans = "GEMINI_API_KEY is not configured.\nPlease configure your Gemini API key before using the AI reasoning service."
        
        audit.log_interaction(
            question=question.strip(),
            tools=[],
            answer=ans,
            confidence="UNRESOLVED",
            evidence=[],
            error=error_info,
            usage=usage.get_usage_stats()
        )
        
        return {
            "answer": ans,
            "confidence": "UNRESOLVED",
            "evidence": [],
            "tools_called": [],
            "usage": usage.get_usage_stats(),
            "error": error_info
        }

    # Prepare Gemini conversation
    contents = [
        {"role": "user", "parts": [{"text": question.strip()}]}
    ]
    tools_called = []
    final_answer = ""
    error_info = None

    try:
        # Multi-turn tool execution loop (max 4 turns)
        max_turns = 4
        for _ in range(max_turns):
            api_res = _call_gemini_api(contents)
            candidates = api_res.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidate response returned by Gemini API.")
                
            first_candidate = candidates[0]
            content = first_candidate.get("content", {})
            parts = content.get("parts", [])
            
            # Check for functionCall parts
            function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
            
            if not function_calls:
                # Terminal answer reached
                text_parts = [p.get("text", "") for p in parts if "text" in p]
                final_answer = "\n".join(text_parts).strip()
                break
                
            # Append model's tool request to contents
            contents.append(content)
            
            # Execute requested functions
            function_response_parts = []
            for fc in function_calls:
                fn_name = fc.get("name")
                fn_args = fc.get("args", {})
                
                tool_exec = _execute_tool_safely(fn_name, fn_args)
                tools_called.append(tool_exec)
                
                function_response_parts.append({
                    "functionResponse": {
                        "name": fn_name,
                        "response": tool_exec["result"]
                    }
                })
                
            # Feed function responses back to Gemini
            contents.append({
                "role": "function",
                "parts": function_response_parts
            })
            
    except Exception as e:
        error_info = {
            "type": "GEMINI_REASONING_ERROR",
            "message": str(e)
        }
        final_answer = f"The finance reasoning service encountered an error while processing your request: {str(e)}"

    # Extract verifiable machine evidence and apply deterministic confidence precedence
    evidence, confidence = _extract_evidence_and_confidence(tools_called)
    
    # Nonexistent transaction graceful response check
    missing_tc = next(
        (tc for tc in tools_called
         if isinstance(tc.get("result"), dict)
         and isinstance(tc["result"].get("error"), dict)
         and tc["result"]["error"].get("type") == "TRANSACTION_NOT_FOUND"),
        None
    )
    if missing_tc:
        confidence = "UNRESOLVED"
        target_id = missing_tc.get("arguments", {}).get("identifier", "")
        if not final_answer or "not found" not in final_answer.lower():
            final_answer = f"Transaction '{target_id}' was not found in the reconciliation dataset. No matching invoice or transaction was found in the available reconciliation data."
        elif target_id and target_id.lower() not in final_answer.lower():
            final_answer = f"Transaction '{target_id}' was not found. {final_answer}"

    # Metering
    success = error_info is None and confidence != "UNRESOLVED"
    usage.record_question_call(success=success)
    
    result_payload = {
        "answer": final_answer,
        "confidence": confidence,
        "evidence": evidence,
        "tools_called": tools_called,
        "usage": usage.get_usage_stats(),
        "error": error_info
    }
    
    # Audit logging
    audit.log_interaction(
        question=question.strip(),
        tools=tools_called,
        answer=final_answer,
        confidence=confidence,
        evidence=evidence,
        error=error_info,
        usage=result_payload["usage"]
    )
    
    return result_payload
