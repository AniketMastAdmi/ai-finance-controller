"""
Dataset Generator for Razorpay AI Finance Controller
Generates deterministic synthetic dataset of:
- 60 invoices (INV1001 to INV1060)
- 63 settlements (SET1001 to SET1063)
Covering 7 deliberate reconciliation categories:
  1. clean_match (36)
  2. fee_deduction (12)
  3. amount_mismatch (3)
  4. timing_gap (3)
  5. missing_settlement (3)
  6. duplicate_settlement (3 invoices -> 6 settlement records)
  7. orphan_settlement (3 settlement records without invoice)
"""

import os
import csv
from datetime import datetime, timedelta

def generate_data(output_dir="."):
    os.makedirs(output_dir, exist_ok=True)
    
    customers = [
        "Acme Corp", "Zenith Tech", "Apex Retail", "CloudScale Inc", 
        "Nexus Logistics", "SolarWave Ltd", "Quantum Health", "Vertex Digital",
        "Global Freight", "Innovate Fin", "BlueHorizon Media", "Starlight Systems",
        "Pinnacle Foods", "CyberShield Security", "Atlas Mobility"
    ]
    
    base_date = datetime(2026, 8, 1)
    
    invoices = []
    settlements = []
    
    # 1. Clean Match (36 invoices: INV1001 - INV1036, SET1001 - SET1036)
    amounts_clean = [
        15000, 24500, 89000, 12000, 45000, 67000, 115000, 32000, 98000, 54000,
        18500, 76000, 29000, 142000, 63000, 37500, 81000, 19500, 51000, 110000,
        22000, 73000, 44000, 160000, 35000, 88000, 27000, 94000, 49000, 125000,
        31000, 68000, 17500, 105000, 58000, 42000
    ]
    
    for i in range(36):
        inv_id = f"INV{1001 + i}"
        set_id = f"SET{1001 + i}"
        cust = customers[i % len(customers)]
        amt = amounts_clean[i]
        inv_dt = base_date + timedelta(days=(i % 15))
        due_dt = inv_dt + timedelta(days=30)
        set_dt = inv_dt + timedelta(days=2 + (i % 3))  # 2-4 days later (within SLA)
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "clean_match"
        })
        
        settlements.append({
            "settlement_id": set_id,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": amt,
            "settlement_date": set_dt.strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_{1001 + i}",
            "payment_method": "netbanking" if i % 2 == 0 else "upi"
        })
        
    # 2. Fee Deduction (12 invoices: INV1037 - INV1048, SET1037 - SET1048)
    # Deductions strictly between 1.0% and 3.5%
    # Borderline cases in [3.0%, 4.0%]: INV1046 (3.2%), INV1047 (3.4%), INV1048 (3.45%)
    fee_percentages = [
        1.10, 1.25, 1.50, 1.75, 2.00, 2.20, 2.50, 2.70, 2.90, 3.20, 3.40, 3.45
    ]
    fee_base_amounts = [
        50000, 80000, 120000, 65000, 95000, 140000, 75000, 110000, 85000, 150000, 200000, 175000
    ]
    
    for i in range(12):
        inv_id = f"INV{1037 + i}"
        set_id = f"SET{1037 + i}"
        cust = customers[(36 + i) % len(customers)]
        amt = fee_base_amounts[i]
        pct = fee_percentages[i]
        deduction = round(amt * (pct / 100.0), 2)
        settled_amt = round(amt - deduction, 2)
        inv_dt = base_date + timedelta(days=5 + (i % 10))
        due_dt = inv_dt + timedelta(days=30)
        set_dt = inv_dt + timedelta(days=3)
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "fee_deduction"
        })
        
        settlements.append({
            "settlement_id": set_id,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": settled_amt,
            "settlement_date": set_dt.strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_{1037 + i}",
            "payment_method": "credit_card"
        })

    # 3. Amount Mismatch (3 invoices: INV1049 - INV1051, SET1049 - SET1051)
    # Deductions > 3.5% (e.g. 7.5%, 12.0%, 20.0% discrepancy/dispute)
    mismatch_amounts = [60000, 130000, 90000]
    mismatch_settled = [55500, 114400, 72000] # (7.5%, 12.0%, 20.0% deduction)
    
    for i in range(3):
        inv_id = f"INV{1049 + i}"
        set_id = f"SET{1049 + i}"
        cust = customers[(48 + i) % len(customers)]
        amt = mismatch_amounts[i]
        settled_amt = mismatch_settled[i]
        inv_dt = base_date + timedelta(days=8 + i)
        due_dt = inv_dt + timedelta(days=30)
        set_dt = inv_dt + timedelta(days=4)
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "amount_mismatch"
        })
        
        settlements.append({
            "settlement_id": set_id,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": settled_amt,
            "settlement_date": set_dt.strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_{1049 + i}",
            "payment_method": "bank_transfer"
        })

    # 4. Timing Gap (3 invoices: INV1052 - INV1054, SET1052 - SET1054)
    # Settlement received 45 to 60 days after invoice date (SLA is 14 days)
    timing_amounts = [48000, 112000, 78000]
    
    for i in range(3):
        inv_id = f"INV{1052 + i}"
        set_id = f"SET{1052 + i}"
        cust = customers[(51 + i) % len(customers)]
        amt = timing_amounts[i]
        inv_dt = base_date + timedelta(days=2 + i)
        due_dt = inv_dt + timedelta(days=30)
        set_dt = inv_dt + timedelta(days=45 + (i * 10))  # 45, 55, 65 days late
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "timing_gap"
        })
        
        settlements.append({
            "settlement_id": set_id,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": amt,
            "settlement_date": set_dt.strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_{1052 + i}",
            "payment_method": "netbanking"
        })

    # 5. Missing Settlement (3 invoices: INV1055 - INV1057, NO SETTLEMENT RECORD)
    missing_amounts = [34000, 82000, 128000]
    for i in range(3):
        inv_id = f"INV{1055 + i}"
        cust = customers[(54 + i) % len(customers)]
        amt = missing_amounts[i]
        inv_dt = base_date + timedelta(days=12 + i)
        due_dt = inv_dt + timedelta(days=30)
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "missing_settlement"
        })
        # No settlement created for missing_settlement

    # 6. Duplicate Settlement (3 invoices: INV1058 - INV1060, each with 2 settlements)
    # Invoices: 3. Settlements created: 6 (SET1055 to SET1060)
    dup_amounts = [56000, 92000, 145000]
    set_counter = 1055
    
    for i in range(3):
        inv_id = f"INV{1058 + i}"
        cust = customers[(57 + i) % len(customers)]
        amt = dup_amounts[i]
        inv_dt = base_date + timedelta(days=10 + i)
        due_dt = inv_dt + timedelta(days=30)
        
        invoices.append({
            "invoice_id": inv_id,
            "customer": cust,
            "invoice_amount": amt,
            "invoice_date": inv_dt.strftime("%Y-%m-%d"),
            "due_date": due_dt.strftime("%Y-%m-%d"),
            "expected_category": "duplicate_settlement"
        })
        
        # 1st settlement
        set_id_1 = f"SET{set_counter}"
        set_counter += 1
        settlements.append({
            "settlement_id": set_id_1,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": amt,
            "settlement_date": (inv_dt + timedelta(days=3)).strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_DUP_{i}_A",
            "payment_method": "upi"
        })
        
        # 2nd duplicate settlement
        set_id_2 = f"SET{set_counter}"
        set_counter += 1
        settlements.append({
            "settlement_id": set_id_2,
            "invoice_id": inv_id,
            "customer": cust,
            "settled_amount": amt,
            "settlement_date": (inv_dt + timedelta(days=4)).strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_PAY_DUP_{i}_B",
            "payment_method": "upi"
        })

    # 7. Orphan Settlements (3 settlements with no matching invoice: SET1061, SET1062, SET1063)
    orphan_amts = [28500, 64000, 118000]
    orphan_custs = ["Unknown Enterprise", "Unregistered Vendor", "Legacy Account Direct"]
    for i in range(3):
        set_id = f"SET{1061 + i}"
        settlements.append({
            "settlement_id": set_id,
            "invoice_id": "UNKNOWN_ORPHAN",
            "customer": orphan_custs[i],
            "settled_amount": orphan_amts[i],
            "settlement_date": (base_date + timedelta(days=15 + i)).strftime("%Y-%m-%d"),
            "gateway_ref": f"RZP_ORPHAN_{1061 + i}",
            "payment_method": "direct_imps"
        })

    # Write invoices.csv
    invoices_file = os.path.join(output_dir, "invoices.csv")
    with open(invoices_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["invoice_id", "customer", "invoice_amount", "invoice_date", "due_date"])
        writer.writeheader()
        for inv in invoices:
            row = {k: v for k, v in inv.items() if k != "expected_category"}
            writer.writerow(row)

    # Write settlements.csv
    settlements_file = os.path.join(output_dir, "settlements.csv")
    with open(settlements_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["settlement_id", "invoice_id", "customer", "settled_amount", "settlement_date", "gateway_ref", "payment_method"])
        writer.writeheader()
        for s in settlements:
            writer.writerow(s)

    print(f"Generated {len(invoices)} invoices -> {invoices_file}")
    print(f"Generated {len(settlements)} settlements -> {settlements_file}")

if __name__ == "__main__":
    generate_data(".")
