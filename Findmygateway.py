import streamlit as st
import pandas as pd

st.set_page_config(page_title="💳 Payment Aggregator Recommender", layout="wide")
st.title("💳 Payment Aggregator Recommender")

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

# --- Sample aggregator dataset ---
data = [
    {"Aggregator": "PayU", 
     "best_for": ["E-commerce", "EdTech", "E-Retail", "OTT"], 
     "gmv_focus": ["1 Cr - 5 Cr", "5 Cr - 25 Cr", "25 Cr and above"],
     "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI", "Wallets"]},

    {"Aggregator": "Razorpay", 
     "best_for": ["E-commerce", "Gaming", "FinTech / InsurTech", "NBFC", "EdTech"], 
     "gmv_focus": ["0 - 25 Lakhs", "25 Lakhs - 1 Cr", "1 Cr - 5 Cr"],
     "methods": ["Credit cards", "Debit cards", "Netbanking", "UPI"]},

    {"Aggregator": "Cashfree", 
     "best_for": ["E-commerce", "Travel", "Food Tech", "AgriTech", "Hyper Local"], 
     "gmv_focus": ["0 - 25 Lakhs", "25 Lakhs - 1 Cr", "1 Cr - 5 Cr"],
     "methods": ["Credit cards", "Debit cards", "UPI", "Wallets"]},

    {"Aggregator": "Billdesk", 
     "best_for": ["Billpay", "Insurance", "BFSI", "Telecom", "Stock Broking"], 
     "gmv_focus": ["5 Cr - 25 Cr", "25 Cr and above"],
     "methods": ["Credit cards", "Debit cards", "Netbanking"]}
]
aggregators = pd.DataFrame(data)

# --- Dropdowns ---
industry = st.selectbox("Select your industry:", industries)
gmv = st.selectbox("Select your average monthly GMV:", gmv_ranges)

# --- Payment methods checkboxes ---
st.markdown("### Select Payment Methods Required")
methods_required = []
for method in ["Credit cards", "Debit cards", "Netbanking", "UPI", "Wallets"]:
    if st.checkbox(method):
        methods_required.append(method)

# --- Recommendation logic ---
if st.button("Get Recommendation"):
    if not industry or not gmv:
        st.warning("Please select both industry and GMV first.")
    else:
        st.subheader("Recommendation")

        scores = []
        for _, row in aggregators.iterrows():
            score = 0

            # Industry match
            if industry in row["best_for"]:
                score += 10

            # GMV match
            if gmv in row["gmv_focus"]:
                score += 5

            # Payment methods match
            if methods_required:
                matched_methods = len(set(methods_required) & set(row["methods"]))
                score += matched_methods * 2

            scores.append({"Aggregator": row["Aggregator"], "Score": score})

        ranked = pd.DataFrame(scores).sort_values(by="Score", ascending=False)
        st.dataframe(ranked, use_container_width=True)

        # Highlight best match
        best_score = ranked["Score"].max()
        best_matches = ranked[ranked["Score"] == best_score]["Aggregator"].tolist()

        if best_score > 0:
            st.success(
                f"🏆 Best Match: **{', '.join(best_matches)}** "
                f"for {industry} with GMV {gmv} and methods {', '.join(methods_required) if methods_required else 'any'}"
            )
        else:
            st.info(
                f"No strong match found for {industry}, GMV {gmv}, and chosen payment methods. "
                "Consider generalist options like PayU or Razorpay."
            )
