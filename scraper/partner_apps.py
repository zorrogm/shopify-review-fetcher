import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from .fallback_parser import extract_fallback_reviews

def parse_review_date(date_str):
    if 'Edited' in date_str:
        date_str = date_str.split('Edited')[1].strip()
    else:
        date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        return None

def scrape_partner_apps(partner_url, start_date, end_date):
    response = requests.get(partner_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    app_links = [a['href'] for a in soup.find_all('a', href=True) if '/apps/' in a['href'] and '/reviews' not in a['href']]
    app_links = list(set(app_links))

    all_reviews = []

    for link in app_links:
        full_url = f"https://apps.shopify.com{link}/reviews?sort_by=newest"
        page = 1
        while True:
            page_url = f"{full_url}&page={page}"
            res = requests.get(page_url)
            soup = BeautifulSoup(res.content, 'html.parser')
            review_divs = soup.find_all("div", attrs={"data-merchant-review": True})

            if not review_divs:
                print(f"⚠️ Fallback triggered for app: {link}")
                fallback_reviews = extract_fallback_reviews(soup)
                for r in fallback_reviews:
                    r["app_name"] = link.split("/")[-1]
                    all_reviews.append(r)
                break

            stop = False
            for div in review_divs:
                try:
                    text_block = div.find('div', {'data-truncate-content-copy': True})
                    review_text = " ".join(p.text.strip() for p in text_block.find_all('p')) if text_block else "N/A"

                    rating_div = div.find("div", {"role": "img"})
                    rating = rating_div["aria-label"].split(" ")[0] if rating_div and "aria-label" in rating_div.attrs else "N/A"

                    name_div = div.find('div', class_='tw-text-heading-xs')
                    reviewer_name = name_div.text.strip() if name_div else "N/A"

                    location, duration = 'N/A', 'N/A'
                    if name_div and name_div.parent:
                        meta_divs = [d for d in name_div.parent.find_all('div') if isinstance(d, Tag)]
                        if len(meta_divs) >= 3:
                            location = meta_divs[1].text.strip()
                            duration = meta_divs[2].text.strip().replace(" using the app", "")

                    date_div = div.find('div', class_='tw-text-body-xs')
                    review_date_str = date_div.text.strip() if date_div else "N/A"
                    review_date = parse_review_date(review_date_str)

                    if review_date and start_date <= review_date <= end_date:
                        all_reviews.append({
                            'app_name': link.split('/')[-1],
                            'review': review_text,
                            'reviewer': reviewer_name,
                            'date': review_date_str,
                            'location': location,
                            'duration': duration,
                            'rating': rating
                        })
                    elif review_date and review_date < end_date:
                        stop = True
                        break
                except Exception:
                    continue
            if stop:
                break
            page += 1
            time.sleep(1)

    return all_reviews
