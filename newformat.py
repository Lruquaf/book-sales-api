import requests
from bs4 import BeautifulSoup
import time
import csv
import os
from datetime import datetime
import chardet

# Base URL for fetching book lists
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# CSV file name
CSV_FILE = f"g1_{datetime.now().strftime('%Y%m%d')}.csv"

# Headers to avoid detection as a bot
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    #"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #"Accept-Language": "en-US,en;q=0.5",
}

def save_to_csv(data, filename=CSV_FILE):
    """Save book data to a CSV file."""
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write the header if file is newly created
        if not file_exists:
            writer.writerow(["ISBN", "DATE", "URL", "BOOK NAME", "WRITER", "TOTAL SALES", "STOCK", "PRICE"])
        
        writer.writerow([
            data.get("isbn"),
            data.get("date"), 
            data.get("url"), 
            data.get("name"), 
            data.get("author"), 
            data.get("total_sales"), 
            data.get("stock"), 
            data.get("price")
        ])


def fetch_book_list(page):
    url = BASE_URL.format(page)
    print(f"📡 Fetching page {page}: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        # ✅ Auto-detect encoding using chardet
        raw_data = response.content
        encoding = chardet.detect(raw_data)["encoding"]
        html = raw_data.decode(encoding or "utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")
        soup.meta["charset"] = "utf-8"  # ✅ Fix HTML meta tag

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    
    books = soup.find_all("div", {"class": "product-cr"})

    if not books:
        print(f"⚠️ No books found on page {page}")
        return []

    return books


def fetch_book_data(url):
    """Fetch detailed data for a single book, skipping those without ISBN."""
    if not url.startswith("http"):
        url = "https://www.kitapyurdu.com" + url
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    try:
        title = soup.find("h1", {"class": "pr_header__heading"}).text.strip()
        isbn_td = soup.find("td", string="ISBN:")
        isbn = isbn_td.find_next("td").text.strip() if isbn_td else None
        
        if not isbn or isbn == "N/A" or isbn.strip() == "":
            print(f"⏩ Skipping book (No ISBN): {title}")
            return None

        # Extract total sales
        sales_element = soup.find("p", {"class": "purchased"})
        total_sales = None
        if sales_element:
            try:
                total_sales = int(sales_element.text.split()[2].replace(".", ""))
            except (ValueError, IndexError):
                total_sales = 0

        # Extract author
        author_element = soup.find("a", {"class": "pr_producers__link"})
        author = author_element.text.strip() if author_element else None

        # Extract price
        price_meta = soup.find("meta", {"itemprop": "price"})
        price = float(price_meta.get("content")) if price_meta else None

        # Extract stock information
        stock = None
        stock_element = soup.find("span", {"class": "stock-info"})
        if stock_element:
            stock_text = stock_element.text.strip()
            if "10+" in stock_text:
                stock = 11
            elif "Stokta" in stock_text:
                stock = int(stock_text.split()[1]) if stock_text.split()[1].isdigit() else None

        return {
            "isbn": isbn,
            "name": title,
            "author": author,
            "price": price,
            "stock": stock,
            "total_sales": total_sales,
            "url": url,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    
    except Exception as e:
        print(f"❌ Error parsing book details: {e}")
        return None

def main():
    """Main function to scrape books and save data to CSV."""
    page = 1
    total_books_fetched = 0
    
    while True:
        books = fetch_book_list(page)
        if not books:
            print("✅ All books fetched successfully!")
            break
        
        for book in books:
            link_element = book.find("a", {"class": "pr-img-link"})
            if link_element and "href" in link_element.attrs:
                book_url = link_element["href"]
                book_data = fetch_book_data(book_url)
                if book_data:
                    print(f"📖 Book Found: {book_data['name']} (ISBN: {book_data['isbn']})")
                    save_to_csv(book_data)
                    total_books_fetched += 1
                else:
                    print("❌ Failed to fetch book data.")
            else:
                print("❌ Link not found!")
        
        page += 1
        time.sleep(2)  # Small delay to avoid getting blocked
    
    print(f"✅ Total {total_books_fetched} books fetched and saved to CSV.")
    


if __name__ == "__main__":
    main()


