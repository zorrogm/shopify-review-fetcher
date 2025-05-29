import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
from datetime import datetime
import time
import random

def fetch_shopify_apps(base_url):
    apps = []
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    divs = soup.select('div.tw-text-body-sm.tw-font-link')
    for div in divs:
        app_name = div.find('a').text.strip()
        app_url = div.find('a')['href']
        if not app_url.startswith('http'):
            app_url = f"https://apps.shopify.com{app_url}"
        apps.append({'name': app_name, 'url': app_url})
    return apps

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

def scrape_partner_apps(base_url, start_date, end_date):
    apps = fetch_shopify_apps(base_url)
    all_reviews = []
    for app in apps:
        app_reviews = []
        base_app_url = app['url'].split('?')[0]
        page = 1
        while True:
            reviews_url = f"{base_app_url}/reviews?sort_by=newest&page={page}"
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

                review_date_div = review_div.find('div', class_='tw-text-body-xs tw-text-fg-tertiary')
                review_date_str = review_date_div.text.strip() if review_date_div else "No review date"

                reviewer_and_location_div = reviewer_name_div.parent
                reviewer_and_location_div_children = [child for child in reviewer_and_location_div.contents if isinstance(child, Tag)]
                location = reviewer_and_location_div_children[1].text.strip() if len(reviewer_and_location_div_children) > 1 else 'N/A'
                duration = reviewer_and_location_div_children[2].text.strip() if len(reviewer_and_location_div_children) > 2 else 'N/A'
                if duration.endswith(' using the app'):
                    duration = duration[:-len(' using the app')]

                rating = extract_rating(review_div)
                review_date = parse_review_date(review_date_str)

                if review_date and review_date > start_date:
                    has_recent_reviews = True
                    continue
                elif review_date and start_date >= review_date >= end_date:
                    app_reviews.append({
                        'app_name': app['name'],
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
            time.sleep(random.uniform(1.2, 3.0))
        all_reviews.extend(app_reviews)
    return all_reviews
