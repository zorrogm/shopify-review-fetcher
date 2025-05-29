from bs4 import BeautifulSoup

def extract_fallback_reviews(html):
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []

    review_blocks = soup.find_all("div", class_="tw-pb-md")
    for block in review_blocks:
        try:
            # Rating via aria-label
            rating_block = block.find("div", {"role": "img", "aria-label": True})
            rating = rating_block['aria-label'].split(" ")[0] if rating_block else "NA"

            # Date: First div with class "tw-text-body-xs" inside the rating container
            date_tag = block.find("div", class_="tw-text-body-xs")
            date = date_tag.get_text(strip=True) if date_tag else "NA"

            # Review text
            review_container = block.find("div", attrs={"data-truncate-review": True})
            review = ""
            if review_container:
                paragraphs = review_container.find_all("p")
                review = " ".join(p.get_text(strip=True) for p in paragraphs)

            # Reviewer
            reviewer_tag = block.find("div", class_="tw-text-heading-xs")
            reviewer = reviewer_tag.get("title", "").strip() if reviewer_tag else "NA"

            # Location and duration
            location, duration = "NA", "NA"
            parent_div = reviewer_tag.find_parent("div") if reviewer_tag else None
            if parent_div:
                all_divs = parent_div.find_all("div")
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if "using the app" in text:
                        duration = text
                    elif text != reviewer:
                        location = text

            reviews.append({
                "reviewer": reviewer,
                "date": date,
                "location": location,
                "duration": duration,
                "rating": rating,
                "review": review
            })
        except Exception as e:
            print(f"⚠️ Error parsing a block: {e}")
            continue

    return reviews