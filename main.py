import streamlit as st
import datetime
from scraper.single_app import scrape_single_app
from scraper.partner_apps import scrape_partner_apps

st.set_page_config(page_title="Shopify Review Fetcher", layout="centered")
st.image("assets/cedlogo.png", width=200)

st.title("📦 Shopify Review Fetcher")
st.markdown("Easily fetch reviews from a single Shopify app or all apps from a partner page.")

mode = st.radio("Choose Mode", ["Single App", "Partner Page"])

url = st.text_input("🔗 Enter the Shopify App or Partner URL")
start_date = st.date_input("Start Date", value=datetime.date(2024, 1, 1))
end_date = st.date_input("End Date", value=datetime.date.today())

if st.button("🚀 Fetch Reviews"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("📡 Please wait while we check Shopify's layout... attempting review scan if needed."):
            try:
                if mode == "Single App":
                    reviews = scrape_single_app(url, start_date, end_date)
                else:
                    reviews = scrape_partner_apps(url, start_date, end_date)

                if not reviews:
                    st.error("No reviews found or unsupported structure. Please verify the URL.")
                else:
                    st.success(f"✅ {len(reviews)} reviews fetched!")
                    st.download_button("📥 Download CSV", data=reviews.to_csv(index=False), file_name="shopify_reviews.csv", mime="text/csv")
            except Exception as e:
                st.error(f"🚨 An error occurred: {e}")