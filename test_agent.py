"""
Unit Test Suite for AI-CFO Reasoning & Reconciliation Layer.
Pins exact dataset ground truths and asserts deterministic behaviors.
Verifies deterministic finance tools, adapter normalization, and Gemini tool calling loop.
"""

try:
    import pytest
except ImportError:
    pytest = None
import os
import tools
import agent
import audit
import usage
from config import UPPER_FEE_TOLERANCE, LOW_CONFIDENCE_LOWER, LOW_CONFIDENCE_UPPER
from adapter import RazorpaySettlementAdapter


def test_get_batch_summary_pinned_metrics():
    """Assert pinned headline reconciliation metrics match ground truth."""
    res = tools.get_batch_summary()
    assert res["success"] is True
    data = res["data"]
    
    # 60 Invoices total
    assert data["total_invoices"] == 60
    # 63 Settlements total
    assert data["total_settlements"] == 63
    # 48 Matched (80.0% Match Rate)
    assert data["matched_invoices"] == 48
    assert data["match_rate_percentage"] == 80.0
    # 12 Invoice Exceptions (20.0% Exception Rate)
    assert data["exception_invoices"] == 12
    assert data["exception_rate_percentage"] == 20.0
    # 3 Orphan Settlements
    assert data["orphan_settlement_count"] == 3
    
    # Category Distribution
    exc_breakdown = data["exception_breakdown"]
    assert exc_breakdown.get("amount_mismatch") == 3
    assert exc_breakdown.get("timing_gap") == 3
    assert exc_breakdown.get("missing_settlement") == 3
    assert exc_breakdown.get("duplicate_settlement") == 3
    
    # Matched Breakdown
    matched_breakdown = data["matched_breakdown"]
    assert matched_breakdown.get("clean_match") == 36
    assert matched_breakdown.get("fee_deduction") == 12


def test_get_transaction_valid_invoice():
    """Assert successful lookup of a valid invoice."""
    res = tools.get_transaction("INV1001")
    assert res["success"] is True
    data = res["data"]
    assert data["invoice_id"] == "INV1001"
    assert data["status"] == "MATCHED"
    assert data["reason"] == "clean_match"
    assert data["confidence"] == "HIGH_CONFIDENCE"


def test_get_transaction_valid_settlement():
    """Assert successful lookup by settlement ID."""
    res = tools.get_transaction("SET1001")
    assert res["success"] is True
    data = res["data"]
    assert data["invoice_id"] == "INV1001"
    assert data["transaction_id"] == "SET1001"


def test_get_transaction_nonexistent():
    """Assert structured error for nonexistent transaction (anti-hallucination)."""
    res = tools.get_transaction("INV9999")
    assert res["success"] is False
    assert res["error"]["type"] == "TRANSACTION_NOT_FOUND"


def test_get_transaction_malformed():
    """Assert structured error for empty or malformed identifier."""
    res = tools.get_transaction("")
    assert res["success"] is False
    assert res["error"]["type"] == "INVALID_IDENTIFIER_FORMAT"


def test_list_exceptions_all():
    """Assert exactly 12 invoice exceptions returned."""
    res = tools.list_exceptions()
    assert res["success"] is True
    assert res["data"]["total_exceptions"] == 12


def test_list_exceptions_by_category():
    """Assert category filtering works accurately."""
    for cat in ["amount_mismatch", "timing_gap", "missing_settlement", "duplicate_settlement"]:
        res = tools.list_exceptions(category=cat)
        assert res["success"] is True
        assert res["data"]["total_exceptions"] == 3
        for exc in res["data"]["exceptions"]:
            assert exc["reason"] == cat


def test_list_exceptions_orphan_category():
    """Assert orphan settlements category filtering."""
    res = tools.list_exceptions(category="orphan_settlement")
    assert res["success"] is True
    assert res["data"]["total_exceptions"] == 3
    for exc in res["data"]["exceptions"]:
        assert exc["reason"] == "orphan_settlement"


def test_get_low_confidence_matches_calculation():
    """Verify low confidence matches logic and boundary conditions."""
    res = tools.get_low_confidence_matches()
    assert res["success"] is True
    matches = res["data"]["matches"]
    
    assert len(matches) > 0
    for m in matches:
        # Must be within 3.0% and 4.0%
        pct = m["deduction_percentage"]
        assert LOW_CONFIDENCE_LOWER <= pct <= LOW_CONFIDENCE_UPPER
        assert m["confidence_level"] == "LOW_CONFIDENCE"
        assert m["review_recommendation"] == "REVIEW_RECOMMENDED"
        assert m["tolerance_boundary"] == UPPER_FEE_TOLERANCE
        # Assert distance calculation
        assert abs(m["distance_from_boundary"] - round(abs(pct - UPPER_FEE_TOLERANCE), 2)) < 0.001


def test_razorpay_settlement_adapter():
    """Verify external Razorpay-style payload normalization."""
    raw_payload = {
        "id": "setl_test_99",
        "entity": "settlement",
        "amount": 50000.0,
        "fee": 1250.0,
        "tax": 225.0,
        "utr": "RZP_UTR_998877",
        "invoice_id": "INV1040",
        "customer": "Acme Corp",
        "created_at": 1725450000
    }
    normalized = RazorpaySettlementAdapter.normalize_record(raw_payload)
    assert normalized["settlement_id"] == "setl_test_99"
    assert normalized["invoice_id"] == "INV1040"
    assert normalized["customer"] == "Acme Corp"
    assert normalized["settled_amount"] == 50000.0
    assert normalized["fee_amount"] == 1250.0
    assert normalized["gateway_ref"] == "RZP_UTR_998877"
    assert normalized["source_format"] == "razorpay_settlement_v1"


def test_gemini_missing_api_key_error():
    """Verify clear configuration error when GEMINI_API_KEY is not configured."""
    original_key = agent.GEMINI_API_KEY
    try:
        agent.GEMINI_API_KEY = ""
        res = agent.ask("Why didn't INV1060 match?")
        assert res["confidence"] == "UNRESOLVED"
        assert "GEMINI_API_KEY is not configured" in res["answer"]
        assert res["error"]["type"] == "CONFIG_ERROR"
    finally:
        agent.GEMINI_API_KEY = original_key


# Mock Gemini handler for deterministic unit testing without external API key
def _mock_gemini_call(contents):
    last = contents[-1]
    if last.get("role") == "function":
        f_resp = last["parts"][0]["functionResponse"]["response"]
        data = f_resp.get("data") or {}
        if not f_resp.get("success", False):
            return {
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Transaction not found. No matching invoice or transaction was found in the available reconciliation data."}]
                    }
                }]
            }
        inv_id = data.get("invoice_id", "INV")
        reason = data.get("reason", "")
        status = data.get("status", "")
        if status == "MATCHED" and reason == "clean_match":
            return {
                "candidates": [{
                    "content": {
                        "parts": [{"text": f"Invoice {inv_id} was successfully MATCHED on time with zero discrepancy."}]
                    }
                }]
            }
        elif reason == "fee_deduction":
            return {
                "candidates": [{
                    "content": {
                        "parts": [{"text": f"Invoice {inv_id} is MATCHED under fee deduction, but flagged LOW_CONFIDENCE (Review Recommended)."}]
                    }
                }]
            }
        elif reason == "duplicate_settlement":
            return {
                "candidates": [{
                    "content": {
                        "parts": [{"text": f"Invoice {inv_id} triggered a DUPLICATE_SETTLEMENT exception with multiple settlements."}]
                    }
                }]
            }
        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": f"Invoice {inv_id} has status {status} with reason {reason}."}]
                }
            }]
        }
    else:
        user_text = contents[0]["parts"][0]["text"].upper()
        if "INV" in user_text:
            import re
            m = re.search(r'INV\d+', user_text)
            ident = m.group(0) if m else "INV1001"
            return {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "functionCall": {
                                "name": "get_transaction",
                                "args": {"identifier": ident}
                            }
                        }]
                    }
                }]
            }
        elif "EXPOSURE" in user_text:
            return {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "functionCall": {
                                "name": "get_batch_summary",
                                "args": {}
                            }
                        }]
                    }
                }]
            }
        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Reconciliation query processed."}]
                }
            }]
        }


def test_gemini_tool_calling_loop_clean_match(monkeypatch):
    """Test Gemini multi-turn tool execution loop for a clean match."""
    orig_key = agent.GEMINI_API_KEY
    orig_call = agent._call_gemini_api
    try:
        agent.GEMINI_API_KEY = "mock_key_for_testing"
        agent._call_gemini_api = _mock_gemini_call
        res = agent.ask("Why didn't INV1001 match?")
        assert "MATCHED" in res["answer"]
        assert res["confidence"] == "HIGH_CONFIDENCE"
        assert len(res["tools_called"]) == 1
        assert res["tools_called"][0]["name"] == "get_transaction"
        assert len(res["evidence"]) > 0
    finally:
        agent.GEMINI_API_KEY = orig_key
        agent._call_gemini_api = orig_call


def test_gemini_tool_calling_loop_duplicate(monkeypatch):
    """Test Gemini multi-turn tool execution loop for a duplicate settlement."""
    orig_key = agent.GEMINI_API_KEY
    orig_call = agent._call_gemini_api
    try:
        agent.GEMINI_API_KEY = "mock_key_for_testing"
        agent._call_gemini_api = _mock_gemini_call
        res = agent.ask("Why didn't INV1060 match?")
        assert "DUPLICATE_SETTLEMENT" in res["answer"]
        assert res["confidence"] == "HIGH_CONFIDENCE"
        assert res["tools_called"][0]["name"] == "get_transaction"
    finally:
        agent.GEMINI_API_KEY = orig_key
        agent._call_gemini_api = orig_call


def test_gemini_tool_calling_loop_low_confidence(monkeypatch):
    """Test Gemini multi-turn tool execution loop for low confidence match."""
    orig_key = agent.GEMINI_API_KEY
    orig_call = agent._call_gemini_api
    try:
        agent.GEMINI_API_KEY = "mock_key_for_testing"
        agent._call_gemini_api = _mock_gemini_call
        res = agent.ask("Why is INV1046 considered a fee deduction?")
        assert res["confidence"] == "LOW_CONFIDENCE"
        assert "LOW_CONFIDENCE" in res["answer"] or "Review Recommended" in res["answer"]
    finally:
        agent.GEMINI_API_KEY = orig_key
        agent._call_gemini_api = orig_call


def test_gemini_tool_calling_loop_nonexistent(monkeypatch):
    """Test Gemini multi-turn tool execution loop for nonexistent transaction."""
    orig_key = agent.GEMINI_API_KEY
    orig_call = agent._call_gemini_api
    try:
        agent.GEMINI_API_KEY = "mock_key_for_testing"
        agent._call_gemini_api = _mock_gemini_call
        res = agent.ask("Why didn't INV9999 match?")
        assert res["confidence"] == "UNRESOLVED"
        assert "not found" in res["answer"].lower()
    finally:
        agent.GEMINI_API_KEY = orig_key
        agent._call_gemini_api = orig_call


def test_audit_logging_and_secret_scrubbing():
    """Test audit log writing and secret redaction."""
    test_q = "Test audit question with secret api_key sk-123456789012345678901234567890"
    res = agent.ask(test_q)
    
    entries = audit.get_audit_trail(limit=5)
    assert len(entries) > 0
    latest = entries[0]
    dumped = str(latest)
    assert "sk-123456789012345678901234567890" not in dumped
    assert "[REDACTED_API_KEY]" in dumped


def test_usage_metering_increments_and_pricing():
    """Test usage metering tracking, compute units, and pricing tiers."""
    initial_stats = usage.get_usage_stats()
    usage.set_pricing_tier(0.15)
    assert usage.get_usage_stats()["pricing_tier_usd"] == 0.15
    usage.set_pricing_tier(0.10)
    
    agent.ask("Test metering increment")
    updated_stats = usage.get_usage_stats()
    assert updated_stats["calls_this_session"] >= initial_stats["calls_this_session"] + 1


if __name__ == "__main__":
    tests = [
        test_get_batch_summary_pinned_metrics,
        test_get_transaction_valid_invoice,
        test_get_transaction_valid_settlement,
        test_get_transaction_nonexistent,
        test_get_transaction_malformed,
        test_list_exceptions_all,
        test_list_exceptions_by_category,
        test_list_exceptions_orphan_category,
        test_get_low_confidence_matches_calculation,
        test_razorpay_settlement_adapter,
        test_gemini_missing_api_key_error,
        test_gemini_tool_calling_loop_clean_match,
        test_gemini_tool_calling_loop_duplicate,
        test_gemini_tool_calling_loop_low_confidence,
        test_gemini_tool_calling_loop_nonexistent,
        test_audit_logging_and_secret_scrubbing,
        test_usage_metering_increments_and_pricing
    ]
    
    print("=" * 60)
    print("RUNNING AI-CFO TEST SUITE (GEMINI ECOSYSTEM)")
    print("=" * 60)
    passed = 0
    
    class MockMonkeyPatch:
        def setattr(self, target, name, value):
            setattr(target, name, value)
            
    mp = MockMonkeyPatch()
    for t in tests:
        try:
            if "monkeypatch" in t.__code__.co_varnames:
                t(mp)
            else:
                t()
            print(f"[PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[FAIL] {t.__name__}: {e}")
            
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed ({passed/len(tests)*100:.1f}%)")
    print("=" * 60)
    if passed != len(tests):
        exit(1)
