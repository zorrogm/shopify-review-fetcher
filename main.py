import streamlit as st
from scraper.single_app import scrape_single_app
from scraper.partner_apps import scrape_partner_apps
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Shopify Review Fetcher", page_icon="📦")

st.image("assets/cedlogo.png", width=200)
st.title("Shopify Review Fetcher")

option = st.radio("What would you like to fetch?", ["Single App Reviews", "All Apps from a Partner"])
url = st.text_input("Enter the Shopify App or Partner URL")
start_date = st.date_input("Start Date", datetime(2025, 5, 9))
end_date = st.date_input("End Date", datetime(2017, 1, 1))

if st.button("Fetch Reviews"):
    with st.spinner("Fetching reviews... this may take a moment."):
        if option == "Single App Reviews":
            reviews = scrape_single_app(url, start_date, end_date)
        else:
            reviews = scrape_partner_apps(url, start_date, end_date)

        if not reviews:
            st.error("No reviews found. Shopify might have changed their layout. Please try again later.")
        else:
            df = pd.DataFrame(reviews)
            csv = df.to_csv(index=False).encode('utf-8')
            st.success("✅ Reviews fetched successfully!")
            st.download_button(label="Download CSV", data=csv, file_name="shopify_reviews.csv", mime="text/csv")
