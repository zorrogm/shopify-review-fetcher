import streamlit as st
from scraper.single_app import scrape_single_app
from scraper.partner_apps import scrape_partner_apps
from datetime import datetime, time
import pandas as pd

st.set_page_config(page_title="Shopify Review Fetcher", page_icon="📦")

st.image("assets/cedlogo.png", width=200)
st.title("Shopify Review Fetcher")

option = st.radio("Select review source:", ["Single App Reviews", "All Apps from a Partner"])
url = st.text_input("Enter the Shopify App or Partner URL")

# Convert date_input values to datetime.datetime objects
start_date_input = st.date_input("Start Date", datetime(2025, 5, 9).date())
end_date_input = st.date_input("End Date", datetime(2017, 1, 1).date())
start_date = datetime.combine(start_date_input, time.min)
end_date = datetime.combine(end_date_input, time.min)

if st.button("Fetch Reviews"):
    if not url:
        st.warning("⚠️ Please enter a valid Shopify App or Partner URL.")
    else:
        st.info("📡 Please wait while we check Shopify's layout... attempting review scan if needed.")
        with st.spinner("🕒 Fetching reviews... This may take 1–3 minutes depending on volume. Please do not close this window."):
            try:
                if option == "Single App Reviews":
                    reviews = scrape_single_app(url, start_date, end_date)
                else:
                    reviews = scrape_partner_apps(url, start_date, end_date)

                if not reviews:
                    st.error("❌ No reviews found. Please check the URL or try a different app/partner.")
                else:
                    df = pd.DataFrame(reviews)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.success("✅ Reviews fetched successfully!")
                    st.download_button(label="📥 Download CSV", data=csv, file_name="shopify_reviews.csv", mime="text/csv")
            except Exception as e:
                st.error(f"🚨 An error occurred: {e}")
