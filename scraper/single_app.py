import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_single_app(url, start_date, end_date):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    if "/reviews" not in url:
        url = url.rstrip("/") + "/reviews"

    all_reviews = []
    page = 1

    while True:
        paginated_url = f"{url}?page={page}&sort_by=newest"
        response = requests.get(paginated_url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        review_blocks = soup.find_all("div", class_="tw-pb-md md:tw-pb-lg tw-mb-md md:tw-mb-lg tw-pt-0 last:tw-pb-0 ")
        if not review_blocks:
            break

        for block in review_blocks:
            try:
                date_text = block.find("div", class_="tw-text-body-xs tw-text-fg-tertiary").text.strip()
                review_date = datetime.strptime(date_text, "%B %d, %Y")
                if review_date.date() < start_date or review_date.date() > end_date:
                    continue

                rating_label = block.find("div", class_="tw-flex tw-items-center tw-justify-between tw-mb-md").find("div", attrs={"aria-label": True})
                rating = rating_label["aria-label"].split(" out")[0] if rating_label else "NA"

                review = block.find("div", {"data-truncate-review": True}).text.strip()

                reviewer = block.find("div", class_="tw-text-heading-xs tw-text-fg-primary tw-overflow-hidden tw-text-ellipsis tw-whitespace-nowrap")
                reviewer = reviewer.text.strip() if reviewer else "NA"

                misc_data = block.find_all("div", class_="tw-order-2 lg:tw-order-1 lg:tw-row-span-2 tw-mt-md md:tw-mt-0 tw-space-y-1 md:tw-space-y-2 tw-text-fg-tertiary  tw-text-body-xs")
                location = duration = "NA"
                if misc_data and len(misc_data[0].find_all("div")) > 2:
                    data_divs = misc_data[0].find_all("div")
                    location = data_divs[1].text.strip()
                    duration = data_divs[2].text.strip()

                all_reviews.append({
                    "reviewer": reviewer,
                    "date": review_date.strftime("%B %d, %Y"),
                    "location": location,
                    "duration": duration,
                    "rating": rating,
                    "review": review
                })
            except Exception:
                continue

        page += 1
        time.sleep(1)

    return pd.DataFrame(all_reviews)