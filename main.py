
import streamlit as st
from datetime import datetime
from scraper.single_app import scrape_single_app
from scraper.partner_apps import scrape_partner_apps

st.set_page_config(page_title="Shopify Review Fetcher", layout="centered")

st.image("assets/cedlogo.png", width=250)

st.title("Shopify App Review Fetcher")

mode = st.radio("Select Mode", ["Single App", "Partner’s All Apps"])

url = st.text_input("Enter the Shopify App or Partner URL")

start_date = st.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.date_input("End Date", datetime.now())

if st.button("Fetch Reviews"):
    if not url:
        st.error("Please enter a valid URL.")
    else:
        with st.spinner("📡 Please wait while we check Shopify's layout... attempting review scan if needed."):
            try:
                if mode == "Single App":
                    reviews = scrape_single_app(url, start_date, end_date)
                else:
                    reviews = scrape_partner_apps(url, start_date, end_date)

                if not reviews:
                    st.warning("No reviews found for the given filters.")
                else:
                    st.success("✅ Reviews fetched successfully. Click below to download.")
                    csv_data = "app_name,review,reviewer,date,rating,duration,location\n"
                    for review in reviews:
                        csv_data += f"{review.get('app_name','')},{review.get('review','').replace(',', ' ')},{review.get('reviewer','')},{review.get('date','')},{review.get('rating','')},{review.get('duration','')},{review.get('location','')}\n"
                    st.download_button("Download CSV", csv_data.encode("utf-8"), "shopify_reviews.csv", "text/csv")
            except Exception as e:
                st.error(f"🚨 An error occurred: {e}")
