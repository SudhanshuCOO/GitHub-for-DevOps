"""
main.py - Book Price Tracker CLI
A web scraping tool that tracks book prices from books.toscrape.com,
stores history in SQLite, and generates reports.

Usage:
    python main.py --scrape              # Scrape and save latest prices
    python main.py --list                # Show all tracked books
    python main.py --drops               # Show price drops
    python main.py --stats               # Show statistics
    python main.py --history <book_id>   # Show price history for a book
    python main.py --export              # Export data to CSV
    python main.py --help                # Show this help message
"""

import argparse
import sys

from database import initialize_db, upsert_book, insert_price
from scraper import scrape_all
from reporter import (
    display_all_books,
    display_price_drops,
    display_stats,
    display_book_history,
    export_to_csv,
)


BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║          📚  Book Price Tracker — books.toscrape.com             ║
║          Built with Python · requests · BeautifulSoup · SQLite   ║
╚══════════════════════════════════════════════════════════════════╝
"""


def run_scrape(num_categories=5, max_pages=2):
    """Scrape books and save them to the database."""
    print("\n[INFO] Starting scrape...\n")
    books = scrape_all(num_categories=num_categories, max_pages_per_category=max_pages)

    if not books:
        print("[ERROR] No books were scraped. Check your internet connection.\n")
        return

    print("\n[DB] Saving to database...")
    saved = 0
    for book in books:
        book_id = upsert_book(
            title=book["title"],
            url=book["url"],
            category=book["category"],
            rating=book["rating"],
        )
        insert_price(
            book_id=book_id,
            price=book["price"],
            availability=book["availability"],
        )
        saved += 1

    print(f"[DB] Saved {saved} price records successfully.\n")
    display_stats()


def main():
    print(BANNER)

    # Initialize database on every run
    initialize_db()

    parser = argparse.ArgumentParser(
        description="📚 Book Price Tracker — Scrape & monitor book prices",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--scrape",
        action="store_true",
        help="Scrape latest book prices from books.toscrape.com",
    )
    parser.add_argument(
        "--categories",
        type=int,
        default=5,
        metavar="N",
        help="Number of categories to scrape (default: 5)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        metavar="N",
        help="Max pages per category to scrape (default: 2)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Display all tracked books and their latest prices",
    )
    parser.add_argument(
        "--drops",
        action="store_true",
        help="Show books with price drops since first tracking",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show summary statistics",
    )
    parser.add_argument(
        "--history",
        type=int,
        metavar="BOOK_ID",
        help="Show full price history for a specific book (use --list to find IDs)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export all tracked data to a CSV file",
    )

    # If no arguments are passed, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.scrape:
        run_scrape(num_categories=args.categories, max_pages=args.pages)

    if args.list:
        display_all_books()

    if args.drops:
        display_price_drops()

    if args.stats:
        display_stats()

    if args.history:
        display_book_history(args.history)

    if args.export:
        export_to_csv()


if __name__ == "__main__":
    main()