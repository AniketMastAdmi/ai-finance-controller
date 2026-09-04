"""
Razorpay Settlement Data Adapter for AI-CFO.
Normalizes external payment gateway settlement records (e.g. Razorpay, Stripe)
into the internal canonical settlement schema consumed by reconciliation tools.
"""

from typing import Dict, Any, List
from datetime import datetime

class RazorpaySettlementAdapter:
    """
    Adapter converting Razorpay-style settlement payloads into internal settlement records.
    
    Standard Razorpay Settlement Payload fields:
    - id: "setl_1001" or "SET1001"
    - entity: "settlement"
    - amount: Gross amount in paise or rupees
    - fee: Platform fee
    - tax: Service tax / GST
    - utr: Bank UTR / Reference number
    - status: "processed"
    - created_at: Unix epoch or ISO timestamp
    """
    
    @staticmethod
    def normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
        # Handle settlement identifier
        settlement_id = raw.get("id") or raw.get("settlement_id") or raw.get("setl_id") or "UNKNOWN_SETTLEMENT"
        
        # Handle invoice link
        invoice_id = raw.get("invoice_id") or raw.get("notes", {}).get("invoice_id") or raw.get("description") or "UNKNOWN_ORPHAN"
        
        # Handle customer name
        customer = raw.get("customer") or raw.get("customer_name") or raw.get("notes", {}).get("customer") or "Unknown Merchant"
        
        # Handle amount (detect paise vs rupees: if > 1000000 and amount ends in 00, or explicitly formatted)
        raw_amt = raw.get("amount") or raw.get("gross_amount") or raw.get("settled_amount") or 0.0
        # If explicitly given in paise as an integer (e.g. 1000000 paise = 10000 INR)
        if isinstance(raw_amt, int) and raw.get("currency") == "INR" and raw_amt > 500000:
            settled_amount = float(raw_amt) / 100.0
        else:
            settled_amount = float(raw_amt)
            
        # Deductions & Net calculations
        fee = float(raw.get("fee", 0.0))
        tax = float(raw.get("tax", 0.0))
        net_credit = raw.get("credit") or (settled_amount - (fee + tax))
        
        # Date conversion
        created_at = raw.get("created_at") or raw.get("settlement_date")
        if isinstance(created_at, (int, float)):
            settlement_date = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d")
        elif isinstance(created_at, str) and "T" in created_at:
            settlement_date = created_at.split("T")[0]
        elif isinstance(created_at, str):
            settlement_date = created_at
        else:
            settlement_date = datetime.now().strftime("%Y-%m-%d")
            
        # Gateway reference / UTR
        gateway_ref = raw.get("utr") or raw.get("gateway_ref") or raw.get("reference_id") or f"RZP_PAY_{settlement_id}"
        payment_method = raw.get("payment_method") or raw.get("method") or "netbanking"
        
        return {
            "settlement_id": str(settlement_id),
            "invoice_id": str(invoice_id),
            "customer": str(customer),
            "settled_amount": float(settled_amount),
            "fee_amount": float(fee),
            "tax_amount": float(tax),
            "net_credit": float(net_credit),
            "settlement_date": str(settlement_date),
            "gateway_ref": str(gateway_ref),
            "payment_method": str(payment_method),
            "source_format": "razorpay_settlement_v1"
        }

    @classmethod
    def normalize_batch(cls, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls.normalize_record(r) for r in records]
