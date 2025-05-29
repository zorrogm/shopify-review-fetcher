
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from .fallback_parser import extract_fallback_reviews

def scrape_single_app(app_url, start_date, end_date):
    reviews = []
    try:
        response = requests.get(app_url)
        soup = BeautifulSoup(response.content, "html.parser")
        review_blocks = soup.find_all("div", {"data-merchant-review": True})

        if not review_blocks:
            return extract_fallback_reviews(app_url, start_date, end_date)

        for block in review_blocks:
            try:
                rating_div = block.find("div", {"role": "img"})
                rating = rating_div.get("aria-label", "").split(" ")[0] if rating_div else "NA"

                date_div = block.find("div", class_="tw-text-body-xs tw-text-fg-tertiary")
                review_date = datetime.strptime(date_div.get_text(strip=True), "%B %d, %Y") if date_div else None

                if review_date and (start_date <= review_date.date() <= end_date):
                    review_text_div = block.find("div", {"data-truncate-review": True})
                    review = review_text_div.get_text(strip=True) if review_text_div else "NA"

                    reviewer_div = block.find("div", {"title": True})
                    reviewer = reviewer_div.get("title", "NA") if reviewer_div else "NA"

                    location = "NA"
                    duration = "NA"
                    info_divs = block.find_all("div", class_="tw-text-body-xs")
                    for div in info_divs:
                        text = div.get_text(strip=True)
                        if "using the app" in text:
                            duration = text
                        elif text not in review and text != review_date.strftime("%B %d, %Y"):
                            location = text

                    reviews.append({
                        "app_name": app_url.split("/")[-1],
                        "review": review,
                        "reviewer": reviewer,
                        "date": review_date.strftime("%B %d, %Y") if review_date else "NA",
                        "rating": rating,
                        "duration": duration,
                        "location": location
                    })
            except Exception:
                continue
        return reviews
    except Exception:
        return extract_fallback_reviews(app_url, start_date, end_date)
