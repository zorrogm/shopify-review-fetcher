from bs4 import Tag

def auto_detect_review_blocks(soup):
    """
    Attempt to auto-locate review containers if Shopify changes DOM structure.
    Returns list of divs that 'look' like reviews.
    """
    fallback_reviews = []

    for div in soup.find_all("div"):
        aria = div.get("aria-label", "")
        p_tags = div.find_all("p")
        if "stars" in aria.lower() and any(len(p.get_text(strip=True)) > 10 for p in p_tags):
            fallback_reviews.append(div)

    return fallback_reviews if len(fallback_reviews) > 2 else []
