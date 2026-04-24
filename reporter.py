"""
reporter.py - Generates reports from tracked book data.
             Supports terminal display and CSV export.
"""

import csv
import os
from datetime import datetime

from database import get_all_books, get_price_drops, get_stats, get_price_history

EXPORTS_DIR = "exports"


def ensure_exports_dir():
    """Create the exports folder if it doesn't exist."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def print_separator(char="─", width=70):
    print(char * width)


def print_header(title):
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def display_all_books():
    """Print a formatted table of all tracked books to the terminal."""
    books = get_all_books()

    if not books:
        print("\n[INFO] No books tracked yet. Run --scrape first.\n")
        return

    print_header("📚  ALL TRACKED BOOKS")
    print(f"  {'#':<4} {'Title':<45} {'Category':<18} {'Price':>8} {'Rating':<8}")
    print_separator()

    for i, book in enumerate(books, 1):
        title = book["title"][:43] + ".." if len(book["title"]) > 43 else book["title"]
        category = book["category"][:16] + ".." if book["category"] and len(book["category"]) > 16 else (book["category"] or "N/A")
        price = f"£{book['latest_price']:.2f}" if book["latest_price"] else "N/A"
        rating = book["rating"] or "N/A"
        print(f"  {i:<4} {title:<45} {category:<18} {price:>8} {rating:<8}")

    print_separator()
    print(f"  Total: {len(books)} books\n")


def display_price_drops():
    """Print books that have dropped in price since first tracking."""
    drops = get_price_drops()

    print_header("📉  PRICE DROPS DETECTED")

    if not drops:
        print("  No price drops found yet. Try scraping multiple times!\n")
        return

    print(f"  {'Title':<40} {'Was':>8} {'Now':>8} {'Drop':>8}")
    print_separator()

    for book in drops:
        title = book["title"][:38] + ".." if len(book["title"]) > 38 else book["title"]
        print(
            f"  {title:<40} "
            f"£{book['original_price']:>6.2f}  "
            f"£{book['current_price']:>6.2f}  "
            f"-£{book['drop_amount']:>5.2f}"
        )

    print_separator()
    print(f"  {len(drops)} price drop(s) found.\n")


def display_stats():
    """Print summary statistics."""
    stats = get_stats()

    print_header("📊  TRACKER STATISTICS")
    print(f"  Total books tracked   : {stats['total_books']}")
    print(f"  Total price snapshots : {stats['total_snapshots']}")
    print(f"  Average latest price  : £{stats['avg_price']:.2f}")

    if stats.get("cheapest") and stats["cheapest"].get("title"):
        cheapest = stats["cheapest"]
        print(f"  Cheapest book        : {cheapest['title'][:40]} — £{cheapest['min_price']:.2f}")

    if stats.get("priciest") and stats["priciest"].get("title"):
        priciest = stats["priciest"]
        print(f"  Most expensive book  : {priciest['title'][:40]} — £{priciest['max_price']:.2f}")

    print_separator()
    print()


def display_book_history(book_id):
    """Print the price history of a specific book by its ID."""
    books = get_all_books()
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        print(f"[ERROR] Book with ID {book_id} not found.\n")
        return

    history = get_price_history(book_id)
    print_header(f"🕐  PRICE HISTORY: {book['title'][:50]}")

    if not history:
        print("  No price history available.\n")
        return

    print(f"  {'Date & Time':<22} {'Price':>8} {'Availability'}")
    print_separator()

    for record in history:
        print(f"  {record['scraped_at']:<22} £{record['price']:>6.2f}  {record['availability']}")

    print_separator()
    print()


def export_to_csv():
    """Export all tracked books to a timestamped CSV file."""
    ensure_exports_dir()
    books = get_all_books()

    if not books:
        print("[INFO] Nothing to export yet. Run --scrape first.\n")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(EXPORTS_DIR, f"books_report_{timestamp}.csv")

    fieldnames = ["id", "title", "category", "rating", "latest_price", "availability", "last_checked", "url"]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(books)

    print(f"[EXPORT] Report saved to: {filename}\n")
    return filename