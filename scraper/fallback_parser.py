from bs4 import Tag
import re

def extract_fallback_reviews(soup):
    """
    Attempt to extract reviews using text-based heuristics if main container fails.
    Adds safety checks and logs for debugging.
    """
    review_blocks = []
    debug_count = 0

    for div in soup.find_all("div"):
        try:
            # Step 1: Find p tags with actual review-like content
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
                    possible_meta = []

                    if name_elem and hasattr(name_elem, "find_parent"):
                        parent = name_elem.find_parent()
                        if parent and isinstance(parent, Tag):
                            meta_divs = parent.find_all("div")
                            if len(meta_divs) >= 3:
                                location = meta_divs[1].get_text(strip=True)
                                duration = meta_divs[2].get_text(strip=True).replace(" using the app", "")

                    review_blocks.append({
                        "review": full_text,
                        "rating": rating,
                        "reviewer": reviewer_name,
                        "date": review_date,
                        "location": location,
                        "duration": duration
                    })
        except Exception as e:
            debug_count += 1
            print(f"[fallback_parser] Block {debug_count} skipped due to error: {e}")
            continue

    print(f"[fallback_parser] Parsed {len(review_blocks)} valid reviews with fallback")
    return review_blocks
