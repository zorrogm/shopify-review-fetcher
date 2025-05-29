from bs4 import Tag

def auto_detect_review_blocks(soup):
    """
    Improved fallback logic to auto-locate Shopify review containers when DOM changes.
    Returns list of divs that resemble review blocks.
    """
    fallback_reviews = []

    for div in soup.find_all("div"):
        try:
            # Heuristic 1: Contains at least 2 <p> tags
            p_tags = div.find_all("p")
            if len(p_tags) >= 2 and any(len(p.get_text(strip=True)) > 10 for p in p_tags):
                # Heuristic 2: Check for text hints like 'stars', 'ago', or rating hints
                text_content = div.get_text(" ", strip=True).lower()
                if any(keyword in text_content for keyword in ["stars", "ago", "rating", "review"]):
                    fallback_reviews.append(div)
        except Exception:
            continue

    print(f"🔥 Fallback detection activated. Found {len(fallback_reviews)} candidate blocks.")
    return fallback_reviews if len(fallback_reviews) > 2 else []
