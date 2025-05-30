import streamlit as st
from datetime import datetime
import pandas as pd
from scraper.single_app import fetch_reviews as fetch_single_app_reviews
from scraper.partner_scraper import fetch_reviews as fetch_partner_reviews, fetch_shopify_apps

st.set_page_config(page_title="Shopify Review Fetcher", layout="centered")

st.title("🛍️ Shopify Review Fetcher")

review_type = st.radio(
    "Select review source:",
    ["Single App Reviews", "All Apps from a Partner"]
)

url = st.text_input("Enter the Shopify App or Partner URL")

start_date = st.date_input("Start Date", datetime.today())
end_date = st.date_input("End Date", datetime(2017, 1, 1))

if st.button("Fetch Reviews"):
    if not url:
        st.error("Please enter a valid Shopify URL.")
    else:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time())

        if review_type == "Single App Reviews":
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

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="shopify_reviews.csv",
            mime='text/csv'
        )
