"""
AI-CFO Reasoning Core for Razorpay AI Finance Controller.
Provider-agnostic reasoning layer that translates financial queries into deterministic tool calls,
constructs verifiable evidence, applies confidence classifications, and maintains complete audit trails.

Directly importable:
    from agent import ask
    result = ask("Why didn't INV1060 match?")
"""

import re
import time
from typing import Dict, Any, List, Optional
import tools
import audit
import usage
from config import AI_PROVIDER, AI_MODEL, AI_API_KEY

SYSTEM_PROMPT = """
You are the AI-CFO Finance Controller Reasoning Layer.
Your role is to explain reconciliation results, identify low-confidence borderline matches, and provide verified evidence for finance operations teams.

Strict Operational Guidelines:
1. Never invent or hallucinate an invoice ID, transaction ID, customer, amount, settlement date, or financial metric.
2. Every answer must be supported by evidence retrieved from deterministic tools.
3. If a transaction is not found, state plainly that it does not exist in the reconciliation records.
4. If a transaction is classified as MATCHED but has a fee deduction near the upper tolerance limit (3.0% - 4.0%), flag it as LOW_CONFIDENCE and recommend human review.
5. Clearly distinguish between facts (tool outputs) and interpretation (reconciliation assessment).
6. Always return confidence level: HIGH_CONFIDENCE, LOW_CONFIDENCE, or UNRESOLVED.
"""

def _extract_identifiers(text: str) -> List[str]:
    """Extract invoice IDs (INVxxxx) or settlement/transaction IDs (SETxxxx, TXNxxxx, RZP_PAY_xxxx)"""
    patterns = [
        r'\bINV\d+\b',
        r'\bSET\d+\b',
        r'\bTXN\d+\b',
        r'\bRZP_PAY_[A-Z0-9_]+\b',
        r'\bRZP_ORPHAN_\d+\b'
    ]
    matches = []
    for p in patterns:
        found = re.findall(p, text, re.IGNORECASE)
        matches.extend([m.upper() for m in found])
    return list(dict.fromkeys(matches))


def _semantic_reasoning(question: str) -> Dict[str, Any]:
    """
    High-precision financial reasoning engine.
    Determines tool execution plan, executes deterministic tools, synthesizes evidence-backed explanations,
    and returns a structured response.
    """
    q_lower = question.lower()
    tools_called = []
    evidence = []
    
    identifiers = _extract_identifiers(question)
    
    # CASE 1: Query about specific invoice or transaction identifier(s)
    if identifiers:
        primary_id = identifiers[0]
        t0 = time.time()
        tool_res = tools.get_transaction(primary_id)
        latency = round((time.time() - t0) * 1000, 2)
        
        tools_called.append({
            "name": "get_transaction",
            "arguments": {"identifier": primary_id},
            "result": tool_res,
            "latency_ms": latency
        })
        
        if not tool_res["success"]:
            # Graceful failure handling for nonexistent transaction
            ans = f"Transaction / Invoice '{primary_id}' was not found in the reconciliation dataset. No matching invoice or settlement record exists in the system."
            return {
                "answer": ans,
                "confidence": "UNRESOLVED",
                "evidence": [],
                "tools_called": tools_called,
                "error": tool_res.get("error")
            }
            
        data = tool_res["data"]
        evidence.append({
            "invoice_id": data["invoice_id"],
            "transaction_id": data["transaction_id"],
            "customer": data["customer"],
            "invoice_amount": data["invoice_amount"],
            "settlement_amount": data["settlement_amount"],
            "status": data["status"],
            "reason": data["reason"],
            "source": tool_res["source"]
        })
        
        status = data["status"]
        reason = data["reason"]
        cust = data["customer"]
        inv_amt = data["invoice_amount"]
        set_amt = data["settlement_amount"]
        pct = data["deduction_percentage"]
        confidence = data.get("confidence", "HIGH_CONFIDENCE")
        
        # Reason synthesis
        if status == "MATCHED":
            if reason == "clean_match":
                ans = (
                    f"Invoice {primary_id} for customer {cust} (₹{inv_amt:,.2f}) was successfully MATCHED. "
                    f"Settlement {data['transaction_id']} was received on time with zero discrepancy (100% payout of ₹{set_amt:,.2f})."
                )
            elif reason == "fee_deduction":
                if confidence == "LOW_CONFIDENCE":
                    ans = (
                        f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) is marked as MATCHED by the reconciliation engine, "
                        f"but our AI-CFO confidence layer flags it as LOW_CONFIDENCE (Review Recommended). "
                        f"The gateway fee deduction is {pct}% (₹{inv_amt - set_amt:,.2f}), which is near the upper tolerance limit of 3.5%. "
                        f"Finance review is recommended to confirm whether this is a legitimate tier fee or an unauthorized discount/short payment."
                    )
                else:
                    ans = (
                        f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) is MATCHED with a standard gateway fee deduction of {pct}% "
                        f"(settled ₹{set_amt:,.2f}, fee ₹{inv_amt - set_amt:,.2f}). This falls safely within the normal 1.0%–3.5% fee tolerance."
                    )
        else: # EXCEPTION
            if reason == "amount_mismatch":
                ans = (
                    f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) failed reconciliation with an AMOUNT_MISMATCH exception. "
                    f"The settled amount was ₹{set_amt:,.2f}, leaving an unexplained variance of ₹{inv_amt - set_amt:,.2f} ({pct}%), "
                    f"which exceeds the allowable 3.5% fee tolerance band."
                )
            elif reason == "timing_gap":
                ans = (
                    f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) resulted in a TIMING_GAP exception. "
                    f"While the settled amount matched (₹{set_amt:,.2f}), settlement took {data['days_to_settle']} days, "
                    f"violating the standard 14-day SLA threshold."
                )
            elif reason == "missing_settlement":
                ans = (
                    f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) is an EXCEPTION due to MISSING_SETTLEMENT. "
                    f"No corresponding payment gateway settlement record has been received in the current batch."
                )
            elif reason == "duplicate_settlement":
                ans = (
                    f"Invoice {primary_id} for {cust} (₹{inv_amt:,.2f}) triggered a DUPLICATE_SETTLEMENT exception. "
                    f"Multiple settlements ({data['transaction_id']}) were received totaling ₹{set_amt:,.2f}. "
                    f"This indicates a potential double disbursement or split settlement requiring immediate review."
                )
            elif reason == "orphan_settlement":
                ans = (
                    f"Settlement {data['transaction_id']} (₹{set_amt:,.2f}) from {cust} is an ORPHAN_SETTLEMENT. "
                    f"Funds were received in the gateway without any matching invoice ID in the ledger."
                )
            else:
                ans = f"Invoice {primary_id} resulted in exception '{reason}': {data['details']}."
                
        return {
            "answer": ans,
            "confidence": confidence,
            "evidence": evidence,
            "tools_called": tools_called,
            "error": None
        }

    # CASE 2: Low-confidence / Risky / Borderline matches question
    if any(k in q_lower for k in ["low confidence", "risky", "borderline", "review recommended", "should i review", "marked matched"]):
        t0 = time.time()
        tool_res = tools.get_low_confidence_matches()
        latency = round((time.time() - t0) * 1000, 2)
        
        tools_called.append({
            "name": "get_low_confidence_matches",
            "arguments": {},
            "result": tool_res,
            "latency_ms": latency
        })
        
        matches = tool_res["data"]["matches"]
        for m in matches:
            evidence.append({
                "invoice_id": m["invoice_id"],
                "transaction_id": m["transaction_id"],
                "customer": m["customer"],
                "invoice_amount": m["invoice_amount"],
                "settled_amount": m["settled_amount"],
                "deduction_percentage": m["deduction_percentage"],
                "distance_from_boundary": m["distance_from_boundary"],
                "source": tool_res["source"]
            })
            
        inv_list = ", ".join([f"{m['invoice_id']} ({m['customer']}: {m['deduction_percentage']}%)" for m in matches])
        ans = (
            f"Identified {len(matches)} low-confidence match(es) that passed the reconciliation engine but sit dangerously close to the 3.5% fee tolerance boundary (3.0% - 4.0%):\n\n"
            f"{inv_list}.\n\n"
            f"The AI-CFO confidence layer recommends manual verification on these transactions to ensure they represent legitimate processing fees rather than concealed discrepancies."
        )
        return {
            "answer": ans,
            "confidence": "HIGH_CONFIDENCE",
            "evidence": evidence,
            "tools_called": tools_called,
            "error": None
        }

    # CASE 3: Category-specific exceptions query (missing, duplicate, timing, mismatch, orphan)
    cat_mapping = {
        "missing": "missing_settlement",
        "duplicate": "duplicate_settlement",
        "timing": "timing_gap",
        "mismatch": "amount_mismatch",
        "orphan": "orphan_settlement"
    }
    
    target_cat = None
    for kw, cat_name in cat_mapping.items():
        if kw in q_lower:
            target_cat = cat_name
            break
            
    if target_cat:
        t0 = time.time()
        tool_res = tools.list_exceptions(target_cat)
        latency = round((time.time() - t0) * 1000, 2)
        
        tools_called.append({
            "name": "list_exceptions",
            "arguments": {"category": target_cat},
            "result": tool_res,
            "latency_ms": latency
        })
        
        excs = tool_res["data"]["exceptions"]
        total_val = sum(e.get("invoice_amount", 0) or e.get("settlement_amount", 0) for e in excs)
        
        for e in excs:
            evidence.append({
                "invoice_id": e.get("invoice_id", "NONE"),
                "transaction_id": e.get("transaction_id", "NONE"),
                "customer": e.get("customer", "UNKNOWN"),
                "amount": e.get("invoice_amount") or e.get("settlement_amount"),
                "reason": target_cat,
                "source": tool_res["source"]
            })
            
        item_labels = []
        for e in excs:
            disp_id = e.get("invoice_id") if e.get("invoice_id") not in (None, "", "NONE") else e.get("transaction_id", "UNKNOWN")
            amt = e.get("invoice_amount") or e.get("settlement_amount", 0.0)
            item_labels.append(f"{disp_id} ({e['customer']}: ₹{amt:,.2f})")
            
        items_str = ", ".join(item_labels)
        ans = (
            f"Found {len(excs)} exception(s) under category '{target_cat}' totaling ₹{total_val:,.2f}:\n\n"
            f"{items_str}."
        )
        return {
            "answer": ans,
            "confidence": "HIGH_CONFIDENCE",
            "evidence": evidence,
            "tools_called": tools_called,
            "error": None
        }

    # CASE 4: Customer-level exception aggregation
    if any(k in q_lower for k in ["customer", "customers", "client", "who has the most"]):
        t0 = time.time()
        tool_res = tools.list_exceptions()
        latency = round((time.time() - t0) * 1000, 2)
        
        tools_called.append({
            "name": "list_exceptions",
            "arguments": {"category": None},
            "result": tool_res,
            "latency_ms": latency
        })
        
        excs = tool_res["data"]["exceptions"]
        cust_counts = {}
        cust_exposure = {}
        for e in excs:
            c = e["customer"]
            cust_counts[c] = cust_counts.get(c, 0) + 1
            cust_exposure[c] = cust_exposure.get(c, 0.0) + e["invoice_amount"]
            
        sorted_custs = sorted(cust_counts.items(), key=lambda x: (x[1], cust_exposure.get(x[0], 0)), reverse=True)
        top_str = "\n".join([f"- **{c}**: {cnt} exception(s), total exposure ₹{cust_exposure[c]:,.2f}" for c, cnt in sorted_custs[:5]])
        
        for e in excs:
            evidence.append({
                "customer": e["customer"],
                "invoice_id": e["invoice_id"],
                "amount": e["invoice_amount"],
                "reason": e["reason"],
                "source": tool_res["source"]
            })
            
        ans = f"Customer exception breakdown across {len(excs)} total exceptions:\n\n{top_str}"
        return {
            "answer": ans,
            "confidence": "HIGH_CONFIDENCE",
            "evidence": evidence,
            "tools_called": tools_called,
            "error": None
        }

    # CASE 5: Exposure, Health, KPIs, or General Batch Summary
    t0 = time.time()
    tool_res = tools.get_batch_summary()
    latency = round((time.time() - t0) * 1000, 2)
    
    tools_called.append({
        "name": "get_batch_summary",
        "arguments": {},
        "result": tool_res,
        "latency_ms": latency
    })
    
    b_data = tool_res["data"]
    evidence.append({
        "total_invoices": b_data["total_invoices"],
        "match_rate": f"{b_data['match_rate_percentage']}%",
        "exception_invoices": b_data["exception_invoices"],
        "total_exception_exposure_inr": b_data["total_exception_exposure_inr"],
        "orphan_settlement_count": b_data["orphan_settlement_count"],
        "source": tool_res["source"]
    })
    
    if any(k in q_lower for k in ["exposure", "value", "rupees", "how much"]):
        ans = (
            f"The total exception exposure for this batch is ₹{b_data['total_exception_exposure_inr']:,.2f} across {b_data['exception_invoices']} exception invoices. "
            f"Additionally, there are {b_data['orphan_settlement_count']} orphan settlements holding ₹{b_data['total_orphan_settlement_value_inr']:,.2f} in unlinked gateway receipts."
        )
    else:
        cats_str = ", ".join([f"{k}: {v}" for k, v in b_data["exception_breakdown"].items()])
        ans = (
            f"Reconciliation Batch Summary:\n"
            f"- **Match Rate**: {b_data['match_rate_percentage']}% ({b_data['matched_invoices']}/{b_data['total_invoices']} invoices matched)\n"
            f"- **Invoice Exceptions**: {b_data['exception_invoices']} invoices ({b_data['exception_rate_percentage']}%)\n"
            f"- **Total Exception Exposure**: ₹{b_data['total_exception_exposure_inr']:,.2f}\n"
            f"- **Orphan Settlements**: {b_data['orphan_settlement_count']} settlements totaling ₹{b_data['total_orphan_settlement_value_inr']:,.2f}\n"
            f"- **Exception Breakdown**: {cats_str}\n"
            f"- **Low-Confidence Matches**: {b_data['low_confidence_match_count']} borderline match(es) recommended for review."
        )
        
    return {
        "answer": ans,
        "confidence": "HIGH_CONFIDENCE",
        "evidence": evidence,
        "tools_called": tools_called,
        "error": None
    }


def ask(question: str) -> Dict[str, Any]:
    """
    Public entry point for AI-CFO reasoning layer.
    Accepts natural language question, coordinates tool calls, logs audit trails, meters usage,
    and returns structured response with answer, confidence, and machine-readable evidence.
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
        
    result = _semantic_reasoning(question.strip())
    
    # Metering
    success = result["confidence"] != "UNRESOLVED" or len(result["tools_called"]) > 0
    usage.record_question_call(success=success)
    result["usage"] = usage.get_usage_stats()
    
    # Audit logging (secret-safe)
    audit.log_interaction(
        question=question.strip(),
        tools=result["tools_called"],
        answer=result["answer"],
        confidence=result["confidence"],
        evidence=result["evidence"],
        error=result["error"],
        usage=result["usage"]
    )
    
    return result
