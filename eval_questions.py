"""
Held-Out Evaluation Suite for AI-CFO Reasoning Layer.
Tests 10 held-out finance questions across all categories:
1. Clean match
2. Standard fee deduction
3. Amount mismatch
4. Timing gap
5. Missing settlement
6. Duplicate settlement
7. Orphan settlement
8. Low-confidence fee deduction
9. Batch-level exposure
10. Nonexistent transaction (anti-hallucination / failure handling)

Measures:
- Question-Answer Accuracy %
- Tool Selection %
- Failure Handling %
- Hallucination Violations (Target: 0)
"""

import sys
import os

# Set UTF-8 stdout if available
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import agent
import tools
from typing import List, Dict, Any

EVALUATION_DATASET = [
    {
        "id": "Q1",
        "category": "clean_match",
        "question": "Why didn't INV1005 match?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1005", "MATCHED", "zero discrepancy"],
        "forbidden_claims": ["EXCEPTION", "missing", "duplicate", "fee_deduction"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q2",
        "category": "fee_deduction",
        "question": "Why is INV1040 considered a fee deduction?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1040", "MATCHED", "fee deduction"],
        "forbidden_claims": ["amount_mismatch", "missing_settlement"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q3",
        "category": "amount_mismatch",
        "question": "Why didn't INV1050 match?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1050", "AMOUNT_MISMATCH", "exceeds"],
        "forbidden_claims": ["clean_match", "timing_gap"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q4",
        "category": "timing_gap",
        "question": "Why did INV1053 fail reconciliation?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1053", "TIMING_GAP", "days", "14"],
        "forbidden_claims": ["clean_match", "missing_settlement"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q5",
        "category": "missing_settlement",
        "question": "What happened to invoice INV1056?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1056", "MISSING_SETTLEMENT", "No corresponding"],
        "forbidden_claims": ["clean_match", "MATCHED"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q6",
        "category": "duplicate_settlement",
        "question": "Why didn't INV1059 match?",
        "expected_tool": "get_transaction",
        "required_facts": ["INV1059", "DUPLICATE_SETTLEMENT", "Multiple"],
        "forbidden_claims": ["clean_match", "missing_settlement"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q7",
        "category": "orphan_settlement",
        "question": "Show me all orphan settlements",
        "expected_tool": "list_exceptions",
        "required_facts": ["orphan", "3", "SET1061"],
        "forbidden_claims": ["clean_match"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q8",
        "category": "low_confidence_fee_deduction",
        "question": "Which transactions should I review even though they are marked matched?",
        "expected_tool": "get_low_confidence_matches",
        "required_facts": ["low-confidence", "tolerance", "INV1046"],
        "forbidden_claims": ["0 matches", "no review required"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q9",
        "category": "batch_exposure",
        "question": "What's my total exception exposure in this batch?",
        "expected_tool": "get_batch_summary",
        "required_facts": ["exposure", "12"],
        "forbidden_claims": ["0 exceptions", "100% matched"],
        "expected_confidence": "HIGH_CONFIDENCE",
        "is_failure_test": False
    },
    {
        "id": "Q10",
        "category": "nonexistent_transaction",
        "question": "Why didn't INV9999 match?",
        "expected_tool": "get_transaction",
        "required_facts": ["not found", "INV9999"],
        "forbidden_claims": ["Acme Corp", "settled on", "fee deduction of 2", "MATCHED with zero"],
        "expected_confidence": "UNRESOLVED",
        "is_failure_test": True
    }
]

def run_evaluation():
    print("=" * 65)
    print("AI-CFO REASONING EVALUATION HARNESS")
    print("=" * 65)
    
    total_q = len(EVALUATION_DATASET)
    passed_q = 0
    correct_tools = 0
    correct_failure_handling = 0
    failure_tests_total = 0
    hallucination_violations = 0
    
    for item in EVALUATION_DATASET:
        qid = item["id"]
        q_text = item["question"]
        exp_tool = item["expected_tool"]
        req_facts = item["required_facts"]
        forb_claims = item["forbidden_claims"]
        exp_conf = item["expected_confidence"]
        is_fail_test = item["is_failure_test"]
        
        if is_fail_test:
            failure_tests_total += 1
            
        res = agent.ask(q_text)
        ans = res["answer"]
        conf = res["confidence"]
        tools_called = [t["name"] for t in res.get("tools_called", [])]
        
        # 1. Tool Selection Check
        tool_ok = exp_tool in tools_called
        if tool_ok:
            correct_tools += 1
            
        # 2. Required Facts Check (case insensitive)
        facts_ok = all(f.lower() in ans.lower() for f in req_facts)
        
        # 3. Forbidden Claims Check (Hallucination check)
        hallucination_found = False
        for f_claim in forb_claims:
            if f_claim.lower() in ans.lower():
                hallucination_violations += 1
                hallucination_found = True
                break
                
        # 4. Confidence check
        conf_ok = (conf == exp_conf)
        
        # 5. Failure test check
        if is_fail_test:
            fail_handled_ok = ("not found" in ans.lower() or "invalid" in ans.lower()) and conf == "UNRESOLVED"
            if fail_handled_ok:
                correct_failure_handling += 1
                
        # Overall Question Pass Criteria
        q_passed = tool_ok and facts_ok and (not hallucination_found) and conf_ok
        if q_passed:
            passed_q += 1
            
        status_str = "PASS" if q_passed else "FAIL"
        tool_sym = "[OK]" if tool_ok else "[X]"
        facts_sym = "[OK]" if facts_ok else "[X]"
        print(f"[{qid}] {status_str} | Tool: {exp_tool} ({tool_sym}) | Confidence: {conf} | Facts: {facts_sym}")
        if not q_passed:
            print(f"     Q: {q_text}")
            print(f"     Ans: {ans[:120]}...")
            
    accuracy_pct = round((passed_q / total_q) * 100.0, 1)
    tool_sel_pct = round((correct_tools / total_q) * 100.0, 1)
    fail_hand_pct = round((correct_failure_handling / failure_tests_total) * 100.0, 1) if failure_tests_total > 0 else 100.0
    
    print("\n" + "=" * 65)
    print("Agent Evaluation")
    print("─────────────────")
    print(f"Questions: {total_q}")
    print(f"Passed: {passed_q}")
    print(f"Failed: {total_q - passed_q}")
    print(f"Accuracy: {accuracy_pct}%\n")
    print(f"Tool selection:\n{tool_sel_pct}%\n")
    print(f"Failure handling:\n{fail_hand_pct}%\n")
    print(f"Hallucination violations:\n{hallucination_violations}")
    print("=" * 65)
    
    return {
        "total_questions": total_q,
        "passed": passed_q,
        "accuracy": accuracy_pct,
        "tool_selection_accuracy": tool_sel_pct,
        "failure_handling_accuracy": fail_hand_pct,
        "hallucination_violations": hallucination_violations
    }

if __name__ == "__main__":
    run_evaluation()
