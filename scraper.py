"""
scraper.py - Scrapes book data from books.toscrape.com (a legal practice website).
"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://books.toscrape.com/"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def get_soup(url):
    """Fetch a page and return a BeautifulSoup object."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not fetch {url}: {e}")
        return None


def get_categories():
    """Scrape and return all book categories with their URLs."""
    print("[SCRAPER] Fetching categories...")
    soup = get_soup(BASE_URL)
    if not soup:
        return []

    category_links = soup.select("ul.nav-list > li > ul > li > a")
    categories = []

    for link in category_links:
        name = link.text.strip()
        url = BASE_URL + link["href"]
        categories.append({"name": name, "url": url})

    print(f"[SCRAPER] Found {len(categories)} categories.")
    return categories


def scrape_books_from_page(page_url, category_name):
    """
    Scrape all books listed on a single catalogue page.
    Returns a list of book dictionaries.
    """
    soup = get_soup(page_url)
    if not soup:
        return []

    books = []
    articles = soup.select("article.product_pod")

    for article in articles:
        try:
            # Title
            title_tag = article.select_one("h3 > a")
            title = title_tag["title"]

            # Relative URL → absolute
            relative_url = title_tag["href"].replace("../", "")
            book_url = BASE_URL + "catalogue/" + relative_url.lstrip("/")

            # Price — strip the £ symbol and convert to float
            price_text = article.select_one("p.price_color").text.strip()
            price = float(price_text.replace("£", "").replace("Â", "").strip())

            # Availability
            availability = article.select_one("p.availability").text.strip()

            # Star rating (stored as a word class, e.g. "Three")
            rating_class = article.select_one("p.star-rating")["class"][1]
            rating_stars = RATING_MAP.get(rating_class, 0)

            books.append({
                "title": title,
                "url": book_url,
                "price": price,
                "availability": availability,
                "rating": f"{rating_stars}/5",
                "category": category_name,
            })
        except Exception as e:
            print(f"  [WARN] Skipped one book due to error: {e}")

    return books


def scrape_category(category_name, category_url, max_pages=3):
    """
    Scrape up to `max_pages` pages from a single category.
    Returns a combined list of books.
    """
    all_books = []
    current_url = category_url
    page_num = 1

    while current_url and page_num <= max_pages:
        print(f"  [SCRAPER] '{category_name}' — page {page_num}...")
        books = scrape_books_from_page(current_url, category_name)
        all_books.extend(books)

        # Check for a "next" button
        soup = get_soup(current_url)
        if soup:
            next_btn = soup.select_one("li.next > a")
            if next_btn:
                # Build the next page URL relative to the category page
                base = current_url.rsplit("/", 1)[0] + "/"
                current_url = base + next_btn["href"]
            else:
                current_url = None
        else:
            current_url = None

        page_num += 1
        time.sleep(0.5)  # Be polite to the server

    return all_books


def scrape_all(num_categories=5, max_pages_per_category=2):
    """
    Main scraping function. Scrapes `num_categories` categories,
    up to `max_pages_per_category` pages each.
    Returns all scraped books as a list of dicts.
    """
    categories = get_categories()
    if not categories:
        print("[ERROR] No categories found. Check your internet connection.")
        return []

    selected = categories[:num_categories]
    all_books = []

    print(f"\n[SCRAPER] Scraping {len(selected)} categories...\n")
    for cat in selected:
        books = scrape_category(cat["name"], cat["url"], max_pages=max_pages_per_category)
        print(f"  → {len(books)} books found in '{cat['name']}'")
        all_books.extend(books)
        time.sleep(1)

    print(f"\n[SCRAPER] Total books scraped: {len(all_books)}")
    return all_books