"""
Deterministic Finance Tools for Razorpay AI Finance Controller.
Performs strictly deterministic operations over the existing reconciliation data.
All calculations are performed here rather than by the LLM.
"""

import os
import csv
from typing import Optional, Dict, Any, List
from config import (
    INVOICES_CSV,
    SETTLEMENTS_CSV,
    RECONCILIATION_REPORT_CSV,
    LOWER_FEE_TOLERANCE,
    UPPER_FEE_TOLERANCE,
    LOW_CONFIDENCE_LOWER,
    LOW_CONFIDENCE_UPPER
)
from usage import record_tool_call

def _load_report() -> List[Dict[str, Any]]:
    if not os.path.exists(RECONCILIATION_REPORT_CSV):
        raise FileNotFoundError(f"Report file not found: {RECONCILIATION_REPORT_CSV}")
    
    rows = []
    with open(RECONCILIATION_REPORT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["invoice_amount"] = float(row["invoice_amount"])
            row["settlement_amount"] = float(row["settlement_amount"])
            row["deduction_percentage"] = float(row["deduction_percentage"]) if row.get("deduction_percentage") else 0.0
            row["days_to_settle"] = int(row["days_to_settle"]) if row.get("days_to_settle") not in (None, "", "-1") else -1
            rows.append(row)
    return rows

def _load_settlements() -> List[Dict[str, Any]]:
    if not os.path.exists(SETTLEMENTS_CSV):
        raise FileNotFoundError(f"Settlements file not found: {SETTLEMENTS_CSV}")
    
    rows = []
    with open(SETTLEMENTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["settled_amount"] = float(row["settled_amount"])
            rows.append(row)
    return rows

def _load_invoices() -> List[Dict[str, Any]]:
    if not os.path.exists(INVOICES_CSV):
        raise FileNotFoundError(f"Invoices file not found: {INVOICES_CSV}")
    
    rows = []
    with open(INVOICES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["invoice_amount"] = float(row["invoice_amount"])
            rows.append(row)
    return rows


def get_transaction(identifier: str) -> Dict[str, Any]:
    """
    Retrieve complete information about one invoice or transaction.
    Supports lookup by invoice_id or transaction_id.
    """
    tool_name = "get_transaction"
    
    if not identifier or not isinstance(identifier, str) or not identifier.strip():
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "INVALID_IDENTIFIER_FORMAT",
                "message": "The provided identifier is empty or malformed."
            }
        }
        
    query_id = identifier.strip().upper()
    
    try:
        report_rows = _load_report()
    except Exception as e:
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "DATA_LOAD_ERROR",
                "message": str(e)
            }
        }
        
    # Search in report by invoice_id or transaction_id
    matched_row = None
    for r in report_rows:
        inv_id = r["invoice_id"].upper()
        txn_ids = [t.strip().upper() for t in r["transaction_id"].split(";")]
        if query_id == inv_id or query_id in txn_ids:
            matched_row = r
            break
            
    # Also check if it's an orphan settlement
    if not matched_row:
        settlements = _load_settlements()
        for s in settlements:
            if s["settlement_id"].upper() == query_id or s.get("gateway_ref", "").upper() == query_id:
                if s.get("invoice_id") == "UNKNOWN_ORPHAN":
                    record_tool_call(tool_name, success=True)
                    return {
                        "success": True,
                        "data": {
                            "invoice_id": "NONE",
                            "transaction_id": s["settlement_id"],
                            "customer": s["customer"],
                            "invoice_amount": 0.0,
                            "settlement_amount": s["settled_amount"],
                            "status": "EXCEPTION",
                            "reason": "orphan_settlement",
                            "deduction_percentage": 0.0,
                            "days_to_settle": -1,
                            "details": f"Orphan settlement received for ₹{s['settled_amount']:,.2f} without matching invoice ID.",
                            "confidence": "HIGH_CONFIDENCE",
                            "review_recommendation": "INVESTIGATE_ORPHAN_FUNDS"
                        },
                        "source": "settlements.csv",
                        "error": None
                    }

    if not matched_row:
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "TRANSACTION_NOT_FOUND",
                "message": f"No invoice or transaction exists with identifier '{identifier}'."
            }
        }
        
    # Determine confidence level
    confidence = "HIGH_CONFIDENCE"
    recommendation = "NONE"
    if matched_row["status"] == "MATCHED" and matched_row["reason"] == "fee_deduction":
        pct = matched_row["deduction_percentage"]
        if LOW_CONFIDENCE_LOWER <= pct <= LOW_CONFIDENCE_UPPER:
            confidence = "LOW_CONFIDENCE"
            recommendation = "REVIEW_RECOMMENDED"
            
    record_tool_call(tool_name, success=True)
    return {
        "success": True,
        "data": {
            "invoice_id": matched_row["invoice_id"],
            "transaction_id": matched_row["transaction_id"],
            "customer": matched_row["customer"],
            "invoice_amount": matched_row["invoice_amount"],
            "settlement_amount": matched_row["settlement_amount"],
            "status": matched_row["status"],
            "reason": matched_row["reason"],
            "deduction_percentage": matched_row["deduction_percentage"],
            "days_to_settle": matched_row["days_to_settle"],
            "details": matched_row["details"],
            "confidence": confidence,
            "review_recommendation": recommendation
        },
        "source": "reconciliation_report.csv",
        "error": None
    }


def list_exceptions(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Return every invoice-level exception with optional category filtering.
    Categories: amount_mismatch, timing_gap, missing_settlement, duplicate_settlement, orphan_settlement
    """
    tool_name = "list_exceptions"
    
    try:
        report_rows = _load_report()
        settlements = _load_settlements()
    except Exception as e:
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "DATA_LOAD_ERROR",
                "message": str(e)
            }
        }
        
    exceptions = [r for r in report_rows if r["status"] == "EXCEPTION"]
    
    # Handle orphan settlements category
    if category and category.strip().lower() in ("orphan_settlement", "orphan", "orphans"):
        orphans = [
            {
                "invoice_id": "NONE",
                "transaction_id": s["settlement_id"],
                "customer": s["customer"],
                "invoice_amount": 0.0,
                "settlement_amount": s["settled_amount"],
                "status": "EXCEPTION",
                "reason": "orphan_settlement",
                "deduction_percentage": 0.0,
                "days_to_settle": -1,
                "details": f"Orphan settlement received on {s['settlement_date']} via {s['payment_method']}."
            }
            for s in settlements if s.get("invoice_id") == "UNKNOWN_ORPHAN"
        ]
        record_tool_call(tool_name, success=True)
        return {
            "success": True,
            "data": {
                "total_exceptions": len(orphans),
                "category_filtered": "orphan_settlement",
                "exceptions": orphans
            },
            "source": "settlements.csv",
            "error": None
        }
        
    if category:
        valid_cat = category.strip().lower()
        filtered = [r for r in exceptions if r["reason"].lower() == valid_cat]
        record_tool_call(tool_name, success=True)
        return {
            "success": True,
            "data": {
                "total_exceptions": len(filtered),
                "category_filtered": valid_cat,
                "exceptions": filtered
            },
            "source": "reconciliation_report.csv",
            "error": None
        }
        
    # Return all exceptions
    record_tool_call(tool_name, success=True)
    return {
        "success": True,
        "data": {
            "total_exceptions": len(exceptions),
            "category_filtered": "ALL",
            "exceptions": exceptions
        },
        "source": "reconciliation_report.csv",
        "error": None
    }


def get_batch_summary() -> Dict[str, Any]:
    """
    Return deterministic batch-level metrics calculated directly from the report and datasets.
    """
    tool_name = "get_batch_summary"
    
    try:
        report_rows = _load_report()
        settlements = _load_settlements()
    except Exception as e:
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "DATA_LOAD_ERROR",
                "message": str(e)
            }
        }
        
    total_invoices = len(report_rows)
    matched_invoices = sum(1 for r in report_rows if r["status"] == "MATCHED")
    exception_invoices = sum(1 for r in report_rows if r["status"] == "EXCEPTION")
    match_rate = round((matched_invoices / total_invoices) * 100.0, 1) if total_invoices > 0 else 0.0
    exception_rate = round((exception_invoices / total_invoices) * 100.0, 1) if total_invoices > 0 else 0.0
    
    # Exception breakdown by category
    categories_breakdown = {}
    total_exception_exposure = 0.0
    for r in report_rows:
        if r["status"] == "EXCEPTION":
            cat = r["reason"]
            categories_breakdown[cat] = categories_breakdown.get(cat, 0) + 1
            total_exception_exposure += r["invoice_amount"]
            
    # Clean vs Fee breakdown
    matched_breakdown = {}
    for r in report_rows:
        if r["status"] == "MATCHED":
            cat = r["reason"]
            matched_breakdown[cat] = matched_breakdown.get(cat, 0) + 1
            
    # Orphan settlements
    orphans = [s for s in settlements if s.get("invoice_id") == "UNKNOWN_ORPHAN"]
    total_orphan_val = sum(s["settled_amount"] for s in orphans)
    
    # Low confidence matches count
    low_conf_matches = [
        r for r in report_rows 
        if r["status"] == "MATCHED" and r["reason"] == "fee_deduction"
        and LOW_CONFIDENCE_LOWER <= r["deduction_percentage"] <= LOW_CONFIDENCE_UPPER
    ]
    
    total_inv_val = sum(r["invoice_amount"] for r in report_rows)
    total_settled_val = sum(s["settled_amount"] for s in settlements)
    
    record_tool_call(tool_name, success=True)
    return {
        "success": True,
        "data": {
            "total_invoices": total_invoices,
            "total_settlements": len(settlements),
            "matched_invoices": matched_invoices,
            "exception_invoices": exception_invoices,
            "match_rate_percentage": match_rate,
            "exception_rate_percentage": exception_rate,
            "matched_breakdown": matched_breakdown,
            "exception_breakdown": categories_breakdown,
            "total_invoice_value_inr": round(total_inv_val, 2),
            "total_settled_value_inr": round(total_settled_val, 2),
            "total_exception_exposure_inr": round(total_exception_exposure, 2),
            "orphan_settlement_count": len(orphans),
            "total_orphan_settlement_value_inr": round(total_orphan_val, 2),
            "low_confidence_match_count": len(low_conf_matches)
        },
        "source": "reconciliation_report.csv",
        "error": None
    }


def get_low_confidence_matches() -> Dict[str, Any]:
    """
    Find every transaction classified as MATCHED with reason fee_deduction
    where deduction_percentage is within 0.5 percentage points of upper tolerance (3.5%),
    i.e. 3.0% <= deduction_percentage <= 4.0%.
    """
    tool_name = "get_low_confidence_matches"
    
    try:
        report_rows = _load_report()
    except Exception as e:
        record_tool_call(tool_name, success=False)
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "DATA_LOAD_ERROR",
                "message": str(e)
            }
        }
        
    flagged = []
    for r in report_rows:
        if r["status"] == "MATCHED" and r["reason"] == "fee_deduction":
            deduction_pct = r["deduction_percentage"]
            if LOW_CONFIDENCE_LOWER <= deduction_pct <= LOW_CONFIDENCE_UPPER:
                distance = round(abs(deduction_pct - UPPER_FEE_TOLERANCE), 2)
                flagged.append({
                    "invoice_id": r["invoice_id"],
                    "transaction_id": r["transaction_id"],
                    "customer": r["customer"],
                    "invoice_amount": r["invoice_amount"],
                    "settled_amount": r["settlement_amount"],
                    "deduction_percentage": deduction_pct,
                    "tolerance_boundary": UPPER_FEE_TOLERANCE,
                    "distance_from_boundary": distance,
                    "confidence_level": "LOW_CONFIDENCE",
                    "review_recommendation": "REVIEW_RECOMMENDED",
                    "reasoning": f"Deduction of {deduction_pct}% is within {distance}% of the {UPPER_FEE_TOLERANCE}% upper fee tolerance limit. Recommended for manual review to verify whether this is genuine fee or an unauthorized discount/short payment."
                })
                
    record_tool_call(tool_name, success=True)
    return {
        "success": True,
        "data": {
            "total_low_confidence_matches": len(flagged),
            "tolerance_boundary": UPPER_FEE_TOLERANCE,
            "boundary_window": f"{LOW_CONFIDENCE_LOWER}% - {LOW_CONFIDENCE_UPPER}%",
            "matches": flagged
        },
        "source": "reconciliation_report.csv",
        "error": None
    }


def get_all_reconciliation_records() -> Dict[str, Any]:
    """Return all reconciliation records from reconciliation_report.csv."""
    try:
        report_rows = _load_report()
        return {
            "success": True,
            "data": {
                "total_records": len(report_rows),
                "records": report_rows
            },
            "source": "reconciliation_report.csv",
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "source": "reconciliation_report.csv",
            "error": {
                "type": "DATA_LOAD_ERROR",
                "message": str(e)
            }
        }

