# 📚 Book Price Tracker

A Python web scraping tool that automatically collects and tracks book prices from [books.toscrape.com](https://books.toscrape.com), stores historical data in a SQLite database, and generates reports with price drop detection.

---

## 🚀 Features

- **Web Scraping** — Scrapes book titles, prices, ratings, categories, and availability using `requests` and `BeautifulSoup4`
- **Price History Tracking** — Every scrape creates a new snapshot, so you can monitor price changes over time
- **Price Drop Detection** — Automatically flags books whose prices have decreased since first tracking
- **SQLite Storage** — Lightweight local database — no setup required
- **CSV Export** — Export all tracked data to a timestamped CSV file
- **Clean CLI Interface** — Simple command-line interface with multiple options

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.8+` | Core language |
| `requests` | HTTP requests to fetch web pages |
| `BeautifulSoup4` | HTML parsing and data extraction |
| `sqlite3` | Built-in database for price history |
| `csv` | Standard library for CSV export |
| `argparse` | Command-line interface |

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/book-price-tracker.git
cd book-price-tracker
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
# Scrape and save latest prices (5 categories, 2 pages each by default)
python main.py --scrape

# Scrape more data — 10 categories, 3 pages each
python main.py --scrape --categories 10 --pages 3

# Display all tracked books with latest prices
python main.py --list

# Show books with price drops
python main.py --drops

# Show summary statistics
python main.py --stats

# Show full price history for a specific book (use --list to find the ID)
python main.py --history 42

# Export all data to a CSV file (saved in exports/)
python main.py --export
```

---

## 📁 Project Structure

```
book_price_tracker/
│
├── main.py          # CLI entry point — handles all user commands
├── scraper.py       # Web scraping logic (requests + BeautifulSoup)
├── database.py      # SQLite operations (CRUD)
├── reporter.py      # Terminal display & CSV export
│
├── requirements.txt # Python dependencies
├── .gitignore       # Git ignore rules
├── exports/         # CSV reports are saved here (auto-created)
└── README.md
```

---

## 📊 Sample Output

```
python main.py --list

  #    Title                                         Category           Price   Rating
  ──────────────────────────────────────────────────────────────────────
  1    A Light in the Attic                          Poetry             £51.77  5/5
  2    Tipping the Velvet                            Historical Fic..   £53.74  1/5
  3    Soumission                                    Fiction            £50.10  1/5
  ...
  Total: 98 books
```

```
python main.py --stats

  Total books tracked   : 98
  Total price snapshots : 196
  Average latest price  : £35.42
  Cheapest book         : Our Band Could Be Your Life — £1.84
  Most expensive book   : The Complete Works of William Sh... — £59.69
```

---

## 🔮 Future Improvements

- [ ] Add email alerts when a price drops below a threshold
- [ ] Schedule automatic daily scrapes using `schedule` or cron
- [ ] Add a simple web dashboard using Flask
- [ ] Extend to scrape real e-commerce sites (Amazon, eBay)
- [ ] Plot price history charts using `matplotlib`

---

## ⚠️ Disclaimer

This project scrapes [books.toscrape.com](https://books.toscrape.com), which is a **sandbox website created specifically for practicing web scraping**. It contains no real products or prices. Always check a website's `robots.txt` and Terms of Service before scraping.

---

## 👤 Author

Built by **[Your Name]** as a portfolio project to demonstrate Python web scraping, data storage, and CLI design skills.

- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [Your LinkedIn](https://linkedin.com)

---

## 📄 License

This project is open source under the [MIT License](LICENSE).