import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="💳 Payment Aggregator Recommender", layout="wide")

# --- Title & Intro ---
st.title("💳 Payment Aggregator Recommender")
st.markdown("""
Welcome! 🎉 This tool helps you discover the **best payment aggregator** for your business. 

👉 Just tell us about your **industry**, **monthly GMV**, and the **payment methods** you need. 

We’ll recommend the aggregator that fits you best using **success rates & pricing** from your dataset.

📂 You can upload either a **JSON file** or a **CSV file** with aggregator data.
""")

# --- File uploader for success rate matrix (JSON or CSV) ---
uploaded_file = st.file_uploader("📂 Upload your success_rate_matrix.json or success_rate_matrix.csv", type=["json", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".json"):
            success_data = json.load(uploaded_file)
            success_df = pd.DataFrame(success_data)
        elif uploaded_file.name.endswith(".csv"):
            success_df = pd.read_csv(uploaded_file)
        else:
            success_df = pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Could not read file: {e}")
        success_df = pd.DataFrame()
else:
    st.info("Using sample dataset for now. Upload your own JSON or CSV file to override.")
    sample_json = [
        {
            "Aggregator": "PayU",
            "best_for": ["E-commerce", "EdTech", "OTT"],
            "gmv_focus": ["1 Cr - 5 Cr", "5 Cr - 25 Cr", "25 Cr and above"],
            "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI", "Wallets"],
            "success_rate_credit_cards": 0.9,
            "success_rate_upi": 0.92,
            "mdr_credit_cards": 0.018,
            "mdr_upi": 0.005
        },
        {
            "Aggregator": "Razorpay",
            "best_for": ["Gaming", "FinTech / InsurTech", "NBFC", "E-commerce"],
            "gmv_focus": ["0 - 25 Lakhs", "25 Lakhs - 1 Cr", "1 Cr - 5 Cr"],
            "methods": ["Credit cards", "Debit cards", "UPI"],
            "success_rate_credit_cards": 0.88,
            "success_rate_upi": 0.9,
            "mdr_credit_cards": 0.02,
            "mdr_upi": 0.007
        }
    ]
    success_df = pd.DataFrame(sample_json)

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

# --- Recommendation logic ---
if st.sidebar.button("✨ Get Recommendation"):
    if industry.strip() == "" or gmv.strip() == "":
        st.warning("⚠️ Please select both industry and GMV first.")
    elif success_df.empty:
        st.warning("⚠️ No success rate data loaded.")
    else:
        st.subheader("🔮 Recommendation Results")

        scores = []
        for _, row in success_df.iterrows():
            score = 0

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
                        if sr_col in row:
                            sr_vals.append(row[sr_col])
                    if sr_vals:
                        score += (sum(sr_vals) / len(sr_vals)) * 10  # normalize

            # Pricing (lower MDR is better)
            if methods_required:
                mdr_vals = []
                for m in methods_required:
                    mdr_col = f"mdr_{m.lower().replace(' ', '_')}"
                    if mdr_col in row:
                        mdr_vals.append(row[mdr_col])
                if mdr_vals:
                    avg_mdr = sum(mdr_vals) / len(mdr_vals)
                    score += max(0, (1 - avg_mdr)) * 5  # reward lower MDR

            scores.append({"Aggregator": row.get("Aggregator", "Unknown"), "Score": score})

        ranked = pd.DataFrame(scores).sort_values(by="Score", ascending=False)
        st.dataframe(ranked, use_container_width=True)

        # Highlight best match
        best_score = ranked["Score"].max()
        best_matches = ranked[ranked["Score"] == best_score]["Aggregator"].tolist()

        if best_score > 0:
            st.success(
                f"🏆 Best Match: **{', '.join(best_matches)}**\\n"
                f"For **{industry}** with GMV **{gmv}** and methods **{', '.join(methods_required) if methods_required else 'any'}**"
            )
        else:
            st.info(
                f"🤔 No strong match found for **{industry}**, GMV **{gmv}**, and chosen methods. "
                "Consider generalist options like **PayU** or **Razorpay**."
            )
