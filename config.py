"""
Configuration module for Razorpay AI Finance Controller.
Central source of truth for:
- File paths
- Fee tolerance bands & Low-confidence thresholds
- Google Gemini LLM settings & Pricing configuration
"""

import os
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR

# File paths
INVOICES_CSV = str(DATA_DIR / "invoices.csv")
SETTLEMENTS_CSV = str(DATA_DIR / "settlements.csv")
RECONCILIATION_REPORT_CSV = str(DATA_DIR / "reconciliation_report.csv")
AUDIT_LOG_FILE = str(DATA_DIR / "audit_log.jsonl")

# Reconciliation & Confidence Thresholds (Single Source of Truth)
# Standard gateway fee tolerance band used by the reconciliation engine
LOWER_FEE_TOLERANCE = 1.0  # 1.0%
UPPER_FEE_TOLERANCE = 3.5  # 3.5%

# Borderline match detection tolerance band
# Flag if within 0.5 percentage points of upper tolerance (3.5%) -> [3.0%, 4.0%]
LOW_CONFIDENCE_DELTA = 0.5
LOW_CONFIDENCE_LOWER = UPPER_FEE_TOLERANCE - LOW_CONFIDENCE_DELTA  # 3.0%
LOW_CONFIDENCE_UPPER = UPPER_FEE_TOLERANCE + LOW_CONFIDENCE_DELTA  # 4.0%

# AI / Provider Settings (Google Gemini Ecosystem)
AI_PROVIDER = "google_gemini"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Commercial Usage Pricing Settings
AI_INVESTIGATION_PRICE_USD = float(os.getenv("AI_INVESTIGATION_PRICE_USD", "0.10"))
USD_TO_INR = float(os.getenv("USD_TO_INR", "85.0"))

# Service Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
