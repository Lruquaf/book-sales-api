from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime
from database import update_book_sales
from database import books_collection


# GÜNCEL URL
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# Selenium başlatma ayarları
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-dev-shm-usage")

def fetch_books():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    page = 1
    total_books_fetched = 0
    isTest = False

    while True:
        url = BASE_URL.format(page)
        print(f"📡 Sayfa {page} taranıyor: {url}")

        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        books = soup.find_all("div", {"class": "product-cr"})
        if not books or isTest:
            print("✅ Tüm kitaplar tarandı, işlem tamamlandı.")
            break

        for book in books:
            try:
                link_element = book.find("a", {"class": "pr-img-link"})
                if link_element and "href" in link_element.attrs:
                    book_data = fetch_book_data(link_element["href"], driver)
                    if book_data:
                        # ✅ Generate and pass date in correct format
                        date = datetime.now().strftime("%d/%m/%Y %H:%M")
                        print(f"📖 Kitap Bulundu: ISBN: {book_data['isbn']}, Adı: {book_data['name']}, Satış: {book_data['total_sales']}")
                        update_book_sales(
                            book_data["isbn"],
                            book_data["name"],
                            book_data["total_sales"],
                            book_data.get("author"),
                            book_data.get("price"),
                            book_data.get("stock"),
                            book_data.get("url"),
                            date  # ✅ Pass date correctly
                        )
                        total_books_fetched += 1
                    else:
                        print("❌ Kitap verisi çekilemedi.")
                else:
                    print("❌ Link bulunamadı!")
            except Exception as e:
                print(f"❌ Kitap verisi çekerken hata oluştu: {e}")

        page += 1

    driver.quit()
    print(f"✅ Toplam {total_books_fetched} kitap başarıyla güncellendi.")

def fetch_book_data(url, driver):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "pr_header__heading"}).text.strip()
        isbn_td = soup.find("td", string="ISBN:")
        isbn = isbn_td.find_next("td").text.strip() if isbn_td else None

        # ✅ Skip only if ISBN is missing
        if not isbn or isbn == "N/A" or isbn.strip() == "":
            print(f"⏩ Kitap atlandı (ISBN yok): {title}")
            return None

        # ✅ Extract total sales (can be None or 0)
        sales_element = soup.find("p", {"class": "purchased"})
        total_sales = None
        if sales_element:
            try:
                total_sales = int(sales_element.text.split()[2].replace(".", ""))
            except (ValueError, IndexError):
                total_sales = None

        # ✅ Extract author safely
        author_element = soup.find("a", {"class": "pr_producers__link"})
        author = author_element.text.strip() if author_element else None

        # ✅ Extract price safely
        price_meta = soup.find("meta", {"itemprop": "price"})
        price = float(price_meta.get("content")) if price_meta else None

        # ✅ Extract stock safely (handles both "10+" and "stokta X ürün var")
        try:
            stock_element = soup.find("span", {"class": "stock-info"})
            if stock_element:
                stock_text = stock_element.text.strip()

                # Handle "Stok miktarı: 10+" case
                if "Stok miktarı" in stock_text:
                    stock = stock_text.replace("Stok miktarı: ", "").strip()
                    if stock == "10+":
                        stock = 11
                    else:
                        stock = int(stock) if stock.isdigit() else None

                # Handle "Stokta X ürün var" case
                elif "Stokta" in stock_text:
                    stock = stock_text.replace("Stokta ", "").replace(" ürün var", "").strip()
                    stock = int(stock) if stock.isdigit() else None
                else:
                    stock = None
            else:
                stock = None
        except Exception as e:
            print(f"❌ Stock extraction error: {e}")
            stock = None



        # ✅ No longer skips books with missing fields
        return {
            "isbn": isbn,
            "name": title,
            "author": author,
            "price": price,
            "stock": stock,
            "total_sales": total_sales,  # Allow None or 0
            "url": url
        }

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


