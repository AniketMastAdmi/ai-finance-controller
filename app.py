"""
AI-CFO Reasoning & Reconciliation Layer — Streamlit Interface
Track 04: AI Finance Controller (Razorpay Hackathon)

A calm, editorial, warm-ivory fintech operations dashboard.
Decoupled architecture: Uses tools.py, agent.py, audit.py, usage.py.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

import tools
import agent
import audit
import usage
from config import UPPER_FEE_TOLERANCE, LOW_CONFIDENCE_LOWER, LOW_CONFIDENCE_UPPER

# Configure Streamlit page
st.set_page_config(
    page_title="AI-CFO | Finance Operations Reasoning Layer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Warm Ivory / Editorial Fintech Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global reset and warm ivory theme */
    .stApp {
        background-color: #FAF9F5;
        color: #242628;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header */
    .cfo-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 24px;
        background-color: #FFFFFF;
        border: 1px solid #EAE7E0;
        border-radius: 8px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .cfo-title {
        font-size: 20px;
        font-weight: 700;
        color: #1A202C;
        letter-spacing: -0.3px;
        margin: 0;
    }
    .cfo-subtitle {
        font-size: 13px;
        color: #64748B;
        margin-top: 3px;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
    }

    /* KPI Summary Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE7E0;
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Section Cards */
    .section-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE7E0;
        border-radius: 8px;
        padding: 22px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 4px;
    }
    .section-desc {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 16px;
    }

    /* Confidence Badges */
    .badge-high {
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #BBF7D0;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-low {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-unresolved {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    /* Answer Card */
    .answer-card {
        background-color: #FFFFFF;
        border: 1px solid #E2DFD8;
        border-left: 4px solid #1E3A8A;
        border-radius: 6px;
        padding: 20px;
        margin-top: 16px;
        margin-bottom: 20px;
    }
    .answer-text {
        font-size: 15px;
        line-height: 1.6;
        color: #1E293B;
    }

    /* Monospace / Code */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="cfo-header">
    <div>
        <h1 class="cfo-title">AI-CFO Reasoning & Finance Controller</h1>
        <div class="cfo-subtitle">API-First Financial Operations & Reconciliation Intelligence Layer</div>
    </div>
    <div class="status-badge">
        <span class="status-dot"></span>
        Operational | Deterministic Tools Synced
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### Navigation")
    nav_option = st.radio(
        "Select View",
        [
            "Overview & Health",
            "Ask AI-CFO",
            "Review Queue (Low Confidence)",
            "Exception Explorer",
            "Audit Trail",
            "API Metering"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### System Configuration")
    st.markdown(f"**Fee Tolerance**: 1.0% – {UPPER_FEE_TOLERANCE}%")
    st.markdown(f"**Review Band**: {LOW_CONFIDENCE_LOWER}% – {LOW_CONFIDENCE_UPPER}%")
    st.markdown("**Engine Mode**: Strict Deterministic")
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: #64748B; line-height: 1.4;">
        <strong>Core Principle</strong><br>
        The reconciliation engine tells you <em>what happened</em>. The AI-CFO explains <em>why</em>, flags borderline risks, and provides audit evidence.
    </div>
    """, unsafe_allow_html=True)

# Load Batch Data
batch_summary = tools.get_batch_summary()["data"]
low_conf_data = tools.get_low_confidence_matches()["data"]

# ==========================================
# 1. OVERVIEW & HEALTH VIEW (ABOVE THE FOLD)
# ==========================================
if nav_option == "Overview & Health":
    st.markdown("### Reconciliation Health (Current Batch)")
    
    # 4 Headline KPI Metrics (Visible in 3 seconds)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Match Rate</div>
            <div class="kpi-value">{batch_summary['match_rate_percentage']}%</div>
            <div class="kpi-sub">{batch_summary['matched_invoices']} of {batch_summary['total_invoices']} Invoices</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Invoice Exceptions</div>
            <div class="kpi-value">{batch_summary['exception_invoices']}</div>
            <div class="kpi-sub">{batch_summary['exception_rate_percentage']}% Exception Rate</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Exception Exposure</div>
            <div class="kpi-value">₹{batch_summary['total_exception_exposure_inr']:,.0f}</div>
            <div class="kpi-sub">Total Capital at Risk</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Orphan Settlements</div>
            <div class="kpi-value">{batch_summary['orphan_settlement_count']}</div>
            <div class="kpi-sub">₹{batch_summary['total_orphan_settlement_value_inr']:,.0f} Unlinked Funds</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Exception Breakdown & Low-Confidence Callout
    c_left, c_right = st.columns([1, 1])
    
    with c_left:
        st.markdown("#### Exception Breakdown by Category")
        exc_df = pd.DataFrame([
            {"Category": k.replace("_", " ").title(), "Count": v}
            for k, v in batch_summary["exception_breakdown"].items()
        ])
        st.dataframe(exc_df, use_container_width=True, hide_index=True)
        
    with c_right:
        st.markdown("#### Low-Confidence Matches (Human Review Required)")
        st.info(
            f"**{low_conf_data['total_low_confidence_matches']} transactions** were classified as `MATCHED` under fee deduction, "
            f"but have deductions near the upper limit ({low_conf_data['boundary_window']}). These may conceal unauthorized discounts or disputes."
        )
        if low_conf_data["matches"]:
            mini_df = pd.DataFrame([
                {
                    "Invoice": m["invoice_id"],
                    "Customer": m["customer"],
                    "Invoice ₹": f"₹{m['invoice_amount']:,.2f}",
                    "Settled ₹": f"₹{m['settled_amount']:,.2f}",
                    "Deduction %": f"{m['deduction_percentage']}%",
                    "Distance": f"{m['distance_from_boundary']}%"
                }
                for m in low_conf_data["matches"]
            ])
            st.dataframe(mini_df, use_container_width=True, hide_index=True)

# ==========================================
# 2. ASK AI-CFO (FINANCIAL REASONING)
# ==========================================
elif nav_option == "Ask AI-CFO":
    st.markdown("### Ask the AI-CFO Reasoning Layer")
    st.caption("Ask natural language finance operations questions. All answers are grounded in deterministic tool evidence.")
    
    # Quick Suggested Prompt Buttons
    st.markdown("**Suggested Investigations:**")
    preset_cols = st.columns(4)
    preset_query = None
    
    with preset_cols[0]:
        if st.button("Why didn't INV1060 match?", use_container_width=True):
            preset_query = "Why didn't INV1060 match?"
    with preset_cols[1]:
        if st.button("Why is INV1046 fee deduction?", use_container_width=True):
            preset_query = "Why is INV1046 considered a fee deduction?"
    with preset_cols[2]:
        if st.button("Which customers have exceptions?", use_container_width=True):
            preset_query = "Which customers have the most exceptions?"
    with preset_cols[3]:
        if st.button("What is our exception exposure?", use_container_width=True):
            preset_query = "What's my total exception exposure in this batch?"

    # Check session state for prepopulated queries
    default_text = preset_query or st.session_state.get("investigate_id", "")
    
    query = st.text_input(
        "Enter your financial inquiry:",
        value=default_text,
        placeholder="e.g. Why didn't INV1050 match? Or show duplicate settlements...",
        key="main_query_input"
    )
    
    submit_clicked = st.button("Reason with AI-CFO", type="primary")
    
    if submit_clicked and query:
        with st.spinner("Executing deterministic finance tools and synthesizing evidence..."):
            response = agent.ask(query)
            
        # Display Answer Box
        badge_class = "badge-high" if response["confidence"] == "HIGH_CONFIDENCE" else ("badge-low" if response["confidence"] == "LOW_CONFIDENCE" else "badge-unresolved")
        badge_label = response["confidence"].replace("_", " ")
        
        st.markdown(f"""
        <div class="answer-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 700; color: #0F172A; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Executive Finding</span>
                <span class="{badge_class}">{badge_label}</span>
            </div>
            <div class="answer-text">{response['answer']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Evidence Section
        if response.get("evidence"):
            st.markdown("#### Verifiable Financial Evidence")
            ev_df = pd.DataFrame(response["evidence"])
            st.dataframe(ev_df, use_container_width=True, hide_index=True)
            
        # Audit Trail (Expandable)
        with st.expander("▸ Audit Trail & Inspection Trace", expanded=False):
            st.markdown(f"**Question**: `{query}`")
            st.markdown(f"**Confidence**: `{response['confidence']}`")
            st.markdown("**Deterministic Tools Called:**")
            for t in response.get("tools_called", []):
                st.markdown(f"- **Tool**: `{t['name']}` | **Latency**: `{t.get('latency_ms', 0)}ms`")
                st.markdown(f"  - **Arguments**: `{json.dumps(t.get('arguments', {}))}`")
                st.json(t.get("result", {}))
            if response.get("error"):
                st.error(f"Error Encountered: {response['error']}")
            st.markdown(f"**Session Usage Snapshot**: `{json.dumps(response.get('usage', {}))}`")

# ==========================================
# 3. REVIEW QUEUE (LOW-CONFIDENCE MATCHES)
# ==========================================
elif nav_option == "Review Queue (Low Confidence)":
    st.markdown("### Review Queue: Low-Confidence Matches")
    st.markdown(
        "These transactions were classified as `MATCHED` by the reconciliation engine under fee deduction, "
        f"but their deduction percentage is within **0.5%** of the upper **{UPPER_FEE_TOLERANCE}%** tolerance limit ({low_conf_data['boundary_window']})."
    )
    
    matches = low_conf_data["matches"]
    
    if not matches:
        st.success("No low-confidence matches in current batch.")
    else:
        for idx, m in enumerate(matches):
            with st.container():
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #EAE7E0; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 16px; font-weight: 700; color: #1E293B;">{m['invoice_id']}</span>
                            <span style="color: #64748B; margin-left: 8px;">— {m['customer']}</span>
                        </div>
                        <span class="badge-low">LOW CONFIDENCE • REVIEW RECOMMENDED</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 12px; font-size: 13px;">
                        <div><strong>Invoice:</strong> ₹{m['invoice_amount']:,.2f}</div>
                        <div><strong>Settled:</strong> ₹{m['settled_amount']:,.2f}</div>
                        <div><strong>Deduction:</strong> <span style="color: #B45309; font-weight: 600;">{m['deduction_percentage']}%</span></div>
                        <div><strong>Boundary Delta:</strong> {m['distance_from_boundary']}% from {m['tolerance_boundary']}%</div>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: #64748B;">
                        <em>{m['reasoning']}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn, _ = st.columns([2, 5])
                with c_btn:
                    if st.button(f"Investigate {m['invoice_id']} with AI-CFO", key=f"btn_rev_{idx}"):
                        st.session_state["investigate_id"] = f"Why is {m['invoice_id']} considered a fee deduction and flagged low confidence?"
                        st.rerun()

# ==========================================
# 4. EXCEPTION EXPLORER
# ==========================================
elif nav_option == "Exception Explorer":
    st.markdown("### Exception Explorer")
    st.caption("Investigate all 12 invoice-level exceptions and 3 orphan settlements.")
    
    cat_filter = st.selectbox(
        "Filter by Exception Category:",
        ["All Categories", "amount_mismatch", "timing_gap", "missing_settlement", "duplicate_settlement", "orphan_settlement"]
    )
    
    cat_param = None if cat_filter == "All Categories" else cat_filter
    exc_result = tools.list_exceptions(category=cat_param)["data"]
    
    st.markdown(f"**Showing {exc_result['total_exceptions']} Exception(s)**")
    
    if exc_result["exceptions"]:
        table_rows = []
        for e in exc_result["exceptions"]:
            inv_amt = e.get("invoice_amount", 0)
            set_amt = e.get("settlement_amount", 0)
            table_rows.append({
                "Invoice ID": e.get("invoice_id", "NONE"),
                "Transaction ID": e.get("transaction_id", "NONE"),
                "Customer": e.get("customer", "UNKNOWN"),
                "Invoice ₹": f"₹{inv_amt:,.2f}" if inv_amt > 0 else "—",
                "Settled ₹": f"₹{set_amt:,.2f}" if set_amt > 0 else "—",
                "Reason": e.get("reason", "").replace("_", " ").title(),
                "Details": e.get("details", "")
            })
            
        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### Quick Investigation")
        inv_to_check = st.selectbox("Select an Exception to Investigate:", [r["Invoice ID"] for r in table_rows if r["Invoice ID"] != "NONE"])
        if st.button("Launch AI Reasoning on Selected Exception"):
            st.session_state["investigate_id"] = f"Why didn't {inv_to_check} match?"
            st.rerun()

# ==========================================
# 5. AUDIT TRAIL
# ==========================================
elif nav_option == "Audit Trail":
    st.markdown("### Immutable Audit Trail")
    st.caption("Chronological, secret-scrubbed record of every AI-CFO reasoning operation.")
    
    entries = audit.get_audit_trail(limit=50)
    
    if not entries:
        st.info("No audit logs recorded yet. Ask a question to generate audit entries.")
    else:
        st.markdown(f"**Total Entries Logged:** {len(entries)}")
        for idx, entry in enumerate(entries):
            ts = entry.get("timestamp", "")
            q = entry.get("question", "")
            conf = entry.get("confidence", "UNKNOWN")
            
            with st.expander(f"[{ts}] {q} — ({conf})"):
                st.markdown(f"**Request ID**: `{entry.get('request_id')}`")
                st.markdown(f"**Answer**: {entry.get('answer')}")
                st.markdown(f"**Confidence**: `{conf}`")
                st.markdown("**Tools Executed:**")
                for t in entry.get("tools", []):
                    st.markdown(f"- `{t.get('name')}` with args `{json.dumps(t.get('arguments', {}))}`")
                    st.json(t.get("result", {}))
                st.markdown("**Machine Evidence Attached:**")
                st.json(entry.get("evidence", []))
                if entry.get("error"):
                    st.error(f"Error: {entry['error']}")

# ==========================================
# 6. API METERING & USAGE
# ==========================================
elif nav_option == "API Metering":
    st.markdown("### API Usage Metering & Operations")
    st.caption("Proof-of-concept metering layer for future usage-based pricing models.")
    
    stats = usage.get_usage_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Questions", stats["calls_this_session"])
    with c2:
        st.metric("Total Tool Calls", stats["total_tool_calls"])
    with c3:
        st.metric("Avg Tools / Question", f"{stats['average_tools_per_question']:.2f}")
    with c4:
        st.metric("Est. Compute Units", f"{stats['estimated_compute_units']}")
        
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Tool Call Distribution")
    tool_df = pd.DataFrame([
        {"Deterministic Tool": k, "Invocations": v}
        for k, v in stats["calls_by_tool"].items()
    ])
    st.dataframe(tool_df, use_container_width=True, hide_index=True)
    
    if st.button("Reset Usage Statistics"):
        usage.reset_usage_stats()
        st.success("Usage stats reset.")
        st.rerun()
