"""
database.py - Handles all SQLite database operations for the Book Price Tracker.
"""

import sqlite3
from datetime import datetime


DB_FILE = "books_tracker.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def initialize_db():
    """Create the necessary tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table to store unique books
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            category TEXT,
            rating TEXT,
            first_seen TEXT NOT NULL
        )
    """)

    # Table to store price snapshots over time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            price REAL NOT NULL,
            availability TEXT,
            scraped_at TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


def upsert_book(title, url, category, rating):
    """
    Insert a new book or ignore if it already exists.
    Returns the book's ID.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO books (title, url, category, rating, first_seen)
        VALUES (?, ?, ?, ?, ?)
    """, (title, url, category, rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()

    # Fetch the ID (works whether it was just inserted or already existed)
    cursor.execute("SELECT id FROM books WHERE url = ?", (url,))
    row = cursor.fetchone()
    conn.close()
    return row["id"]


def insert_price(book_id, price, availability):
    """Save a new price snapshot for a book."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO price_history (book_id, price, availability, scraped_at)
        VALUES (?, ?, ?, ?)
    """, (book_id, price, availability, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_all_books():
    """Return all tracked books with their latest price."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.id,
            b.title,
            b.category,
            b.rating,
            b.url,
            b.first_seen,
            ph.price AS latest_price,
            ph.availability,
            ph.scraped_at AS last_checked
        FROM books b
        LEFT JOIN price_history ph ON ph.id = (
            SELECT id FROM price_history
            WHERE book_id = b.id
            ORDER BY scraped_at DESC
            LIMIT 1
        )
        ORDER BY b.title
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_price_history(book_id):
    """Return full price history for a specific book."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT price, availability, scraped_at
        FROM price_history
        WHERE book_id = ?
        ORDER BY scraped_at ASC
    """, (book_id,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_price_drops():
    """
    Find books where the latest price is lower than the first recorded price.
    Returns books with a price drop.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.title,
            b.category,
            first_ph.price AS original_price,
            last_ph.price AS current_price,
            ROUND(first_ph.price - last_ph.price, 2) AS drop_amount,
            b.url
        FROM books b
        JOIN price_history first_ph ON first_ph.id = (
            SELECT id FROM price_history WHERE book_id = b.id ORDER BY scraped_at ASC LIMIT 1
        )
        JOIN price_history last_ph ON last_ph.id = (
            SELECT id FROM price_history WHERE book_id = b.id ORDER BY scraped_at DESC LIMIT 1
        )
        WHERE last_ph.price < first_ph.price
        ORDER BY drop_amount DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """Return summary statistics from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM price_history")
    total_snapshots = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT AVG(ph.price) AS avg_price
        FROM price_history ph
        WHERE ph.id IN (
            SELECT MAX(id) FROM price_history GROUP BY book_id
        )
    """)
    avg_price = cursor.fetchone()["avg_price"]

    cursor.execute("""
        SELECT MIN(ph.price) AS min_price, b.title
        FROM price_history ph
        JOIN books b ON b.id = ph.book_id
        WHERE ph.id IN (
            SELECT MAX(id) FROM price_history GROUP BY book_id
        )
    """)
    cheapest = cursor.fetchone()

    cursor.execute("""
        SELECT MAX(ph.price) AS max_price, b.title
        FROM price_history ph
        JOIN books b ON b.id = ph.book_id
        WHERE ph.id IN (
            SELECT MAX(id) FROM price_history GROUP BY book_id
        )
    """)
    priciest = cursor.fetchone()

    conn.close()

    return {
        "total_books": total_books,
        "total_snapshots": total_snapshots,
        "avg_price": round(avg_price, 2) if avg_price else 0,
        "cheapest": dict(cheapest) if cheapest else {},
        "priciest": dict(priciest) if priciest else {},
    }