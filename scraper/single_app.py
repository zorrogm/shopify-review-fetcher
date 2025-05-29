import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
from datetime import datetime
import time

def extract_rating(review):
    rating_div = review.find('div', class_='tw-flex tw-relative tw-space-x-0.5 tw-w-[88px] tw-h-md')
    if rating_div and 'aria-label' in rating_div.attrs:
        aria_label = rating_div['aria-label']
        try:
            return aria_label.split(' ')[0]
        except IndexError:
            return None
    return None

def parse_review_date(date_str):
    if 'Edited' in date_str:
        date_str = date_str.split('Edited')[1].strip()
    else:
        date_str = date_str.split('Edited')[0].strip()
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        return None

def scrape_single_app(app_url, start_date, end_date):
    base_url = app_url.split('?')[0]
    page = 1
    reviews = []

    while True:
        reviews_url = f"{base_url}/reviews?sort_by=newest&page={page}"
        response = requests.get(reviews_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        review_divs = soup.find_all("div", attrs={"data-merchant-review": True})

        if not review_divs:
            break

        has_recent_reviews = False
        for review_div in review_divs:
            review_text_div = review_div.find('div', {'data-truncate-content-copy': True})
            review_text = review_text_div.find('p').text.strip() if review_text_div else "No review text"

            reviewer_name_div = review_div.find('div', class_='tw-text-heading-xs tw-text-fg-primary tw-overflow-hidden tw-text-ellipsis tw-whitespace-nowrap')
            reviewer_name = reviewer_name_div.text.strip() if reviewer_name_div else "No reviewer name"

            reviewer_and_location_div = reviewer_name_div.parent
            reviewer_and_location_div_children = [child for child in reviewer_and_location_div.contents if isinstance(child, Tag)]
            location = reviewer_and_location_div_children[1].text.strip() if len(reviewer_and_location_div_children) > 1 else 'N/A'
            duration = reviewer_and_location_div_children[2].text.strip() if len(reviewer_and_location_div_children) > 2 else 'N/A'
            if duration.endswith(' using the app'):
                duration = duration[:-len(' using the app')]

            review_date_div = review_div.find('div', class_='tw-text-body-xs tw-text-fg-tertiary')
            review_date_str = review_date_div.text.strip() if review_date_div else "No review date"
            rating = extract_rating(review_div)
            review_date = parse_review_date(review_date_str)

            if review_date and review_date > start_date:
                has_recent_reviews = True
                continue
            elif review_date and start_date >= review_date >= end_date:
                reviews.append({
                    'app_name': app_url.split('/')[-1],
                    'review': review_text,
                    'reviewer': reviewer_name,
                    'date': review_date_str,
                    'location': location,
                    'duration': duration,
                    'rating': rating
                })
                has_recent_reviews = True
            else:
                break

        if not has_recent_reviews:
            break
        page += 1
        time.sleep(1)

    return reviews
