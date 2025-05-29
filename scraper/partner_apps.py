import requests
from bs4 import BeautifulSoup, Tag
import re
import time
from datetime import datetime
from urllib.parse import urljoin

def scrape_partner_apps(partner_url, start_date, end_date):
    print("📡 Please wait while we check Shopify's layout... attempting review scan if needed.")
    response = requests.get(partner_url)
    soup = BeautifulSoup(response.content, "html.parser")

    app_cards = soup.find_all("a", class_=re.compile("tw-block tw-border"))

    app_urls = []
    for card in app_cards:
        href = card.get("href")
        if href and "/apps/" in href:
            full_url = urljoin("https://apps.shopify.com", href)
            app_urls.append(full_url)

    all_reviews = []

    for app_url in app_urls:
        app_name = app_url.split("/")[-1]
        page = 1

        while True:
            url = app_url.rstrip("/") + "/reviews?page=" + str(page)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            review_divs = soup.find_all("div", class_=re.compile("tw-border-b"))

            if not review_divs:
                print(f"⚠️ Layout changed for {app_name}. Trying fallback mode...")
                fallback_reviews = []
                for div in soup.find_all("div"):
                    try:
                        p_tags = div.find_all("p")
                        if len(p_tags) >= 2:
                            full_text = " ".join(p.get_text(strip=True) for p in p_tags).lower()
                            if any(k in full_text for k in ["support", "app", "feature", "integration", "problem", "recommend"]):
                                rating_elem = div.find("div", {"role": "img", "aria-label": re.compile(r"\d out of 5 stars")})
                                rating = rating_elem["aria-label"].split(" ")[0] if rating_elem else "N/A"

                                date_elem = div.find("div", class_=re.compile("tw-text-body-xs"))
                                review_date = date_elem.get_text(strip=True) if date_elem else "N/A"

                                name_elem = div.find("div", class_=re.compile("tw-text-heading-xs"))
                                reviewer_name = name_elem.get_text(strip=True) if name_elem else "N/A"

                                location = "N/A"
                                duration = "N/A"
                                if name_elem:
                                    try:
                                        parent = name_elem.find_parent()
                                        if parent and isinstance(parent, Tag):
                                            meta_divs = parent.find_all("div")
                                            if len(meta_divs) >= 3:
                                                location = meta_divs[1].get_text(strip=True)
                                                duration = meta_divs[2].get_text(strip=True).replace(" using the app", "")
                                    except Exception as inner_e:
                                        print(f"[inline fallback] Meta parse failed: {inner_e}")

                                fallback_reviews.append({
                                    'app_name': app_name,
                                    'review': full_text,
                                    'reviewer': reviewer_name,
                                    'date': review_date,
                                    'location': location,
                                    'duration': duration,
                                    'rating': rating
                                })
                    except Exception as e:
                        print(f"[inline fallback] Block skipped: {e}")
                        continue
                all_reviews.extend(fallback_reviews)
                break

            for div in review_divs:
                try:
                    review = div.find("p").get_text(strip=True)
                    rating_elem = div.find("div", {"role": "img", "aria-label": re.compile(r"\d out of 5 stars")})
                    rating = rating_elem["aria-label"].split(" ")[0] if rating_elem else "N/A"
                    date_elem = div.find("div", class_=re.compile("tw-text-body-xs"))
                    review_date = date_elem.get_text(strip=True) if date_elem else "N/A"
                    name_elem = div.find("div", class_=re.compile("tw-text-heading-xs"))
                    reviewer_name = name_elem.get_text(strip=True) if name_elem else "N/A"
                    meta = div.find_all("div", class_=re.compile("tw-text-body-xs"))
                    location = meta[1].get_text(strip=True) if len(meta) > 1 else "N/A"
                    duration = meta[2].get_text(strip=True).replace(" using the app", "") if len(meta) > 2 else "N/A"

                    parsed_date = datetime.strptime(review_date, "%B %d, %Y").date()
                    if parsed_date > start_date:
                        all_reviews.append({
                            'app_name': app_name,
                            'review': review,
                            'reviewer': reviewer_name,
                            'date': review_date,
                            'location': location,
                            'duration': duration,
                            'rating': rating
                        })
                except Exception:
                    continue

            if not soup.find("a", text="Next"):
                break
            page += 1
            time.sleep(1.2)

    return all_reviews
