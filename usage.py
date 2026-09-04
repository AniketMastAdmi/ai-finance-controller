"""
Usage Metering & Commercial Pricing Layer for AI-CFO Reasoning Agent.
Tracks session invocations, tool breakdown, failure rates, and proof-of-concept billing metrics.
Supports dynamic investigation pricing tiers ($0.05, $0.10, $0.15) and INR conversion.
"""

from datetime import datetime, timezone
import threading
from config import AI_INVESTIGATION_PRICE_USD, USD_TO_INR

class UsageTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self.session_start_time = datetime.now(timezone.utc).isoformat()
        self.calls_this_session = 0
        self.total_tool_calls = 0
        self.failed_calls = 0
        self.pricing_tier_usd = AI_INVESTIGATION_PRICE_USD
        self.usd_to_inr = USD_TO_INR
        self.calls_by_tool = {
            "get_transaction": 0,
            "list_exceptions": 0,
            "get_batch_summary": 0,
            "get_low_confidence_matches": 0,
            "get_all_reconciliation_records": 0
        }
        
    def record_tool_call(self, tool_name: str, success: bool = True):
        with self._lock:
            self.total_tool_calls += 1
            if tool_name in self.calls_by_tool:
                self.calls_by_tool[tool_name] += 1
            else:
                self.calls_by_tool[tool_name] = 1
                
            if not success:
                self.failed_calls += 1

    def record_question_call(self, success: bool = True):
        with self._lock:
            self.calls_this_session += 1
            if not success:
                self.failed_calls += 1

    def set_pricing_tier(self, tier_usd: float):
        with self._lock:
            self.pricing_tier_usd = float(tier_usd)

    def get_usage_stats(self) -> dict:
        with self._lock:
            avg_tools = round(self.total_tool_calls / self.calls_this_session, 2) if self.calls_this_session > 0 else 0.0
            cost_usd = round(self.calls_this_session * self.pricing_tier_usd, 2)
            cost_inr = round(cost_usd * self.usd_to_inr, 2)
            return {
                "session_start_time": self.session_start_time,
                "calls_this_session": self.calls_this_session,
                "total_tool_calls": self.total_tool_calls,
                "calls_by_tool": dict(self.calls_by_tool),
                "failed_calls": self.failed_calls,
                "average_tools_per_question": avg_tools,
                "estimated_compute_units": round(self.calls_this_session * 1.0 + self.total_tool_calls * 0.25, 2),
                "pricing_tier_usd": self.pricing_tier_usd,
                "usd_to_inr_rate": self.usd_to_inr,
                "estimated_usage_cost_usd": cost_usd,
                "estimated_usage_cost_inr": cost_inr
            }

    def reset(self):
        with self._lock:
            self.session_start_time = datetime.now(timezone.utc).isoformat()
            self.calls_this_session = 0
            self.total_tool_calls = 0
            self.failed_calls = 0
            self.calls_by_tool = {
                "get_transaction": 0,
                "list_exceptions": 0,
                "get_batch_summary": 0,
                "get_low_confidence_matches": 0,
                "get_all_reconciliation_records": 0
            }

# Global singleton tracker
_tracker = UsageTracker()

def record_tool_call(tool_name: str, success: bool = True):
    _tracker.record_tool_call(tool_name, success)

def record_question_call(success: bool = True):
    _tracker.record_question_call(success)

def set_pricing_tier(tier_usd: float):
    _tracker.set_pricing_tier(tier_usd)

def get_usage_stats() -> dict:
    return _tracker.get_usage_stats()

def reset_usage_stats():
    _tracker.reset()
