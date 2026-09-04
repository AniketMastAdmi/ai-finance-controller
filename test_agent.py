"""
Unit Test Suite for AI-CFO Reasoning & Reconciliation Layer.
Pins exact dataset ground truths and asserts deterministic behaviors.
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


def test_agent_ask_clean_match():
    """Test AI reasoning for a clean match."""
    res = agent.ask("Why didn't INV1001 match?")
    assert "MATCHED" in res["answer"]
    assert res["confidence"] == "HIGH_CONFIDENCE"
    assert len(res["evidence"]) > 0


def test_agent_ask_duplicate_settlement():
    """Test AI reasoning for a duplicate settlement."""
    res = agent.ask("Why didn't INV1060 match?")
    assert "DUPLICATE_SETTLEMENT" in res["answer"] or "duplicate" in res["answer"].lower()
    assert res["confidence"] == "HIGH_CONFIDENCE"
    assert len(res["evidence"]) > 0


def test_agent_ask_low_confidence_match():
    """Test AI reasoning for borderline fee deduction."""
    res = agent.ask("Why is INV1046 considered a fee deduction?")
    assert res["confidence"] == "LOW_CONFIDENCE"
    assert "Review Recommended" in res["answer"] or "LOW_CONFIDENCE" in res["answer"]


def test_agent_ask_nonexistent_transaction():
    """Test anti-hallucination on missing transaction."""
    res = agent.ask("Why didn't INV9999 match?")
    assert "not found" in res["answer"].lower()
    assert res["confidence"] == "UNRESOLVED"


def test_audit_logging_and_secret_scrubbing():
    """Test audit log writing and secret redaction."""
    test_q = "Test audit question with secret api_key sk-123456789012345678901234567890"
    res = agent.ask(test_q)
    
    entries = audit.get_audit_trail(limit=5)
    assert len(entries) > 0
    latest = entries[0]
    # Ensure raw secret sk-... is not leaked in audit log
    dumped = str(latest)
    assert "sk-123456789012345678901234567890" not in dumped
    assert "[REDACTED_API_KEY]" in dumped


def test_usage_metering_increments():
    """Test usage metering tracking."""
    initial_stats = usage.get_usage_stats()
    agent.ask("What is my total exception exposure?")
    updated_stats = usage.get_usage_stats()
    
    assert updated_stats["calls_this_session"] >= initial_stats["calls_this_session"] + 1
    assert updated_stats["total_tool_calls"] >= initial_stats["total_tool_calls"] + 1


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
        test_agent_ask_clean_match,
        test_agent_ask_duplicate_settlement,
        test_agent_ask_low_confidence_match,
        test_agent_ask_nonexistent_transaction,
        test_audit_logging_and_secret_scrubbing,
        test_usage_metering_increments
    ]
    
    print("=" * 60)
    print("RUNNING AI-CFO TEST SUITE")
    print("=" * 60)
    passed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed ({passed/len(tests)*100:.1f}%)")
    print("=" * 60)
    if passed != len(tests):
        exit(1)

