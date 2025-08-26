import streamlit as st
import pandas as pd

st.set_page_config(page_title="💳 Payment Aggregator Recommender", layout="wide")

# --- Title & Intro ---
st.title("💳 Payment Aggregator Recommender")
st.markdown(
    """
Welcome! 🎉 This tool helps you discover the **best payment aggregator or direct bank gateway** for your business.

👉 Select your **industry**, **monthly GMV**, and **payment methods**. Optionally tick **competitive pricing** if you prefer direct bank stacks for very high GMV.

We’ll recommend options using a small embedded dataset (POC).
"""
)

# --- Backend dataset embedded directly in code (POC sample) ---
success_data = [
    {
        "Aggregator": "PayU",
        "type": "aggregator",
        "bank_stack": "Multi-acquirer (sample)",
        "best_for": ["E-commerce", "EdTech", "OTT"],
        "gmv_focus": ["1 Cr - 5 Cr", "5 Cr - 25 Cr", "25 Cr and above"],
        "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI", "Wallets"],
        "success_rate_credit_cards": 0.90,
        "success_rate_debit_cards": 0.88,
        "success_rate_upi": 0.92,
        "success_rate_netbanking": 0.87,
        "mdr_credit_cards": 0.018,
        "mdr_debit_cards": 0.017,
        "mdr_upi": 0.005,
        "mdr_netbanking": 0.015
    },
    {
        "Aggregator": "Razorpay",
        "type": "aggregator",
        "bank_stack": "Multi-acquirer (sample)",
        "best_for": ["Gaming", "FinTech / InsurTech", "NBFC", "E-commerce"],
        "gmv_focus": ["0 - 25 Lakhs", "25 Lakhs - 1 Cr", "1 Cr - 5 Cr"],
        "methods": ["Credit cards", "Debit cards", "UPI"],
        "success_rate_credit_cards": 0.88,
        "success_rate_debit_cards": 0.86,
        "success_rate_upi": 0.90,
        "mdr_credit_cards": 0.020,
        "mdr_debit_cards": 0.019,
        "mdr_upi": 0.007
    },
    {
        "Aggregator": "Cashfree",
        "type": "aggregator",
        "bank_stack": "Multi-acquirer (sample)",
        "best_for": ["Travel", "Food Tech", "AgriTech", "Hyper Local"],
        "gmv_focus": ["0 - 25 Lakhs", "25 Lakhs - 1 Cr", "1 Cr - 5 Cr"],
        "methods": ["Credit cards", "UPI", "Wallets", "BNPL"],
        "success_rate_credit_cards": 0.87,
        "success_rate_upi": 0.91,
        "success_rate_bnpl": 0.89,
        "mdr_credit_cards": 0.021,
        "mdr_upi": 0.006,
        "mdr_bnpl": 0.022
    },
    # --- Direct Bank Gateways (for enterprise/high GMV) ---
    {
        "Aggregator": "HDFC SmartGateway",
        "type": "bank_gateway",
        "bank_stack": "HDFC Bank",
        "best_for": ["E-commerce", "BFSI", "Travel", "OTT", "EdTech"],
        "gmv_focus": ["5 Cr - 25 Cr", "25 Cr and above"],
        "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI"],
        "success_rate_credit_cards": 0.92,
        "success_rate_debit_cards": 0.91,
        "success_rate_upi": 0.93,
        "success_rate_netbanking": 0.90,
        "mdr_credit_cards": 0.017,
        "mdr_debit_cards": 0.016,
        "mdr_upi": 0.0045,
        "mdr_netbanking": 0.012
    },
    {
        "Aggregator": "Axis UniPG",
        "type": "bank_gateway",
        "bank_stack": "Axis Bank",
        "best_for": ["E-commerce", "Travel", "BFSI", "EdTech"],
        "gmv_focus": ["5 Cr - 25 Cr", "25 Cr and above"],
        "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI"],
        "success_rate_credit_cards": 0.91,
        "success_rate_debit_cards": 0.90,
        "success_rate_upi": 0.93,
        "success_rate_netbanking": 0.89,
        "mdr_credit_cards": 0.0175,
        "mdr_debit_cards": 0.0165,
        "mdr_upi": 0.0048,
        "mdr_netbanking": 0.0125
    }
]
success_df = pd.DataFrame(success_data)

# --- Industry list ---
industries = [
    "E-commerce", "Gaming", "Hyper Local", "Billpay", "Travel", "BFSI",
    "E-Retail", "Telecom", "AgriTech", "NBFC", "E-Pharma", "Stock Broking",
    "Insurance", "Ticketing", "OTT", "Hyperlocal", "Classified",
    "Travel & Hospitality", "FinTech / InsurTech", "Food Tech", "Other",
    "Media / Telecom / OTT", "EdTech"
]

# --- GMV ranges ---
gmv_ranges = [
    "0 - 25 Lakhs",
    "25 Lakhs - 1 Cr",
    "1 Cr - 5 Cr",
    "5 Cr - 25 Cr",
    "25 Cr and above"
]

# --- Sidebar for inputs ---
st.sidebar.header("🔧 Configure Your Business")
industry = st.sidebar.selectbox("Select your industry", [" "] + industries, index=0)
gmv = st.sidebar.selectbox("Select your average monthly GMV", [" "] + gmv_ranges, index=0)

st.sidebar.markdown("### Select Payment Methods Required")
methods_required = []
all_methods = ["Credit cards", "Debit cards", "Netbanking", "UPI", "Wallets", "BNPL", "Standing instruction"]
for method in all_methods:
    if st.sidebar.checkbox(method):
        methods_required.append(method)

prefer_bank_pricing = st.sidebar.checkbox(
    "Optimize for most competitive pricing (bank direct)",
    help="Tick this if you prefer direct bank stacks for high GMV with bespoke pricing."
)

# --- Recommendation logic ---
if st.sidebar.button("✨ Get Recommendation"):
    if industry.strip() == "" or gmv.strip() == "":
        st.warning("⚠️ Please select both industry and GMV first.")
    elif success_df.empty:
        st.warning("⚠️ No success rate data available.")
    else:
        st.subheader("🔮 Recommendation Results")

        scores = []
        for _, row in success_df.iterrows():
            score = 0.0

            # Industry match
            if industry in row.get("best_for", []):
                score += 10

            # GMV match
            if gmv in row.get("gmv_focus", []):
                score += 5

            # Payment methods match using success rates
            if methods_required:
                matched_methods = set(methods_required) & set(row.get("methods", []))
                if matched_methods:
                    sr_vals = []
                    for m in matched_methods:
                        sr_col = f"success_rate_{m.lower().replace(' ', '_')}"
                        if sr_col in row and pd.notna(row[sr_col]):
                            sr_vals.append(float(row[sr_col]))
                    if sr_vals:
                        score += (sum(sr_vals) / len(sr_vals)) * 10  # success-rate boost

            # Pricing (lower MDR is better)
            if methods_required:
                mdr_vals = []
                for m in methods_required:
                    mdr_col = f"mdr_{m.lower().replace(' ', '_')}"
                    if mdr_col in row and pd.notna(row[mdr_col]):
                        mdr_vals.append(float(row[mdr_col]))
                if mdr_vals:
                    avg_mdr = sum(mdr_vals) / len(mdr_vals)
                    score += max(0, (1 - avg_mdr)) * 5  # reward lower MDR

            # Enterprise pricing preference (for very high GMV)
            if prefer_bank_pricing and gmv == "25 Cr and above":
                if row.get("type") == "bank_gateway":
                    score += 8  # boost direct bank options for high GMV

            scores.append({
                "Aggregator": row.get("Aggregator", "Unknown"),
                "Bank Stack": row.get("bank_stack", "-"),
                "Type": row.get("type", "aggregator"),
                "Score": round(score, 3)
            })

        ranked = pd.DataFrame(scores).sort_values(by="Score", ascending=False)

        # Merge a few extra fields for display (like methods)
        display_df = ranked.merge(
            success_df[["Aggregator", "methods"]], on="Aggregator", how="left"
        )
        st.dataframe(display_df, use_container_width=True)

        # Highlight best match
        best_score = ranked["Score"].max()
        best_matches = ranked[ranked["Score"] == best_score]["Aggregator"].tolist()

        if best_score > 0:
            st.success(
                f"🏆 Best Match: **{', '.join(best_matches)}**\n"
                f"For **{industry}** with GMV **{gmv}** and methods **{', '.join(methods_required) if methods_required else 'any'}**"
            )
        else:
            st.info(
                f"🤔 No strong match found for **{industry}**, GMV **{gmv}**, and chosen methods. "
                "Consider generalist options like **PayU** or **Razorpay**."
            )
