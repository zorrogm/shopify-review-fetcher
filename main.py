import streamlit as st
from datetime import datetime
import pandas as pd
from scraper.single_app import fetch_reviews as fetch_single_app_reviews
from scraper.partner_scraper import fetch_reviews as fetch_partner_reviews, fetch_shopify_apps

st.set_page_config(page_title="Shopify Review Fetcher", layout="centered")

st.markdown("## 🛍️ Shopify Review Fetcher")
st.caption("Easily download reviews from any Shopify app or partner's portfolio.")

st.markdown("### 🔍 What would you like to fetch?")
review_type = st.radio(
    "",
    ["Reviews from a specific Shopify App", "Reviews from all apps by a Shopify Partner"]
)

url = st.text_input("🔗 Paste the Shopify App or Partner URL")

start_date = st.date_input("📅 Start Date", datetime.today())
end_date = st.date_input("📅 End Date", datetime(2017, 1, 1))

if st.button("🔎 Fetch Reviews"):
    if not url:
        st.error("Please enter a valid Shopify URL.")
    else:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time())

        with st.spinner("⏳ Fetching reviews... please wait"):
            if review_type == "Reviews from a specific Shopify App":
                app_name = url.split('/')[-1].split('?')[0].replace('-', ' ').title()
                reviews = fetch_single_app_reviews(url, app_name, start_dt, end_dt, debug=False)
            else:
                apps = fetch_shopify_apps(url)
                reviews = []
                for app in apps:
                    app_reviews = fetch_partner_reviews(app['url'], app['name'], start_dt, end_dt)
                    reviews.extend(app_reviews)

        df = pd.DataFrame(reviews)
        st.success(f"✅ Fetched {len(df)} reviews.")
        st.dataframe(df)

        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="shopify_reviews.csv",
                mime='text/csv'
            )
