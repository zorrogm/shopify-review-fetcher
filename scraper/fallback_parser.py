from bs4 import Tag
import re

def extract_fallback_reviews(soup):
    """
    Attempt to extract reviews using text-based heuristics if main container fails.
    """
    review_blocks = []

    for div in soup.find_all("div"):
        try:
            # Look for blocks with multiple <p> tags and keywords in text
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

                    possible_meta = name_elem.find_parent().find_all("div") if name_elem else []
                    if len(possible_meta) >= 3:
                        location = possible_meta[1].get_text(strip=True)
                        duration = possible_meta[2].get_text(strip=True).replace(" using the app", "")

                    review_blocks.append({
                        "review": full_text,
                        "rating": rating,
                        "reviewer": reviewer_name,
                        "date": review_date,
                        "location": location,
                        "duration": duration
                    })
        except Exception:
            continue

    return review_blocks
