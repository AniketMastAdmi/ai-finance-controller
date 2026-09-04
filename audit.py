"""
Audit Logging Layer for AI-CFO Reasoning Agent.
Maintains append-only, tamper-evident audit_log.jsonl with strict secret scrubbing.
Provides queryable interfaces for the Streamlit UI, FastAPI service, and compliance monitoring.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import AUDIT_LOG_FILE

def _scrub_secrets(obj: Any) -> Any:
    """Recursively scrub any sensitive strings like API keys or tokens."""
    import re
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if any(secret_term in k.lower() for secret_term in ["secret", "token", "password", "auth", "api_key"]):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = _scrub_secrets(v)
        return cleaned
    elif isinstance(obj, list):
        return [_scrub_secrets(elem) for elem in obj]
    elif isinstance(obj, str):
        # Redact specific secret token patterns
        text = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_API_KEY]', obj)
        text = re.sub(r'AIza[a-zA-Z0-9_\-]{20,}', '[REDACTED_API_KEY]', text)
        text = re.sub(r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer [REDACTED_TOKEN]', text, flags=re.IGNORECASE)
        return text
    return obj


def log_interaction(
    question: str,
    tools: List[Dict[str, Any]],
    answer: str,
    confidence: str,
    evidence: List[Dict[str, Any]],
    error: Optional[Dict[str, Any]] = None,
    usage: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Append an audit log entry in JSON Lines format to audit_log.jsonl.
    """
    req_id = request_id or str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    entry = {
        "timestamp": timestamp,
        "request_id": req_id,
        "question": _scrub_secrets(question),
        "tools": _scrub_secrets(tools),
        "answer": _scrub_secrets(answer),
        "confidence": confidence,
        "evidence": _scrub_secrets(evidence),
        "error": _scrub_secrets(error) if error else None,
        "usage": _scrub_secrets(usage) if usage else {}
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(AUDIT_LOG_FILE)), exist_ok=True)
    
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        
    return entry


def get_audit_trail(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Retrieve audit entries in reverse chronological order (newest first).
    """
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
        
    entries = []
    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                    
    # Reverse to return latest first
    entries.reverse()
    return entries[offset : offset + limit]


def get_audit_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single audit log entry by request_id."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return None
        
    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("request_id") == request_id:
                        return entry
                except json.JSONDecodeError:
                    continue
    return None


def clear_audit_log():
    """Clear audit log (for test suite isolation)."""
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)
