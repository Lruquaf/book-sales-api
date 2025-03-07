from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from database import update_book_sales

# GÜNCEL URL
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/search&sort=purchased_365&order=DESC&filter_name=dogan%20kitap&filter_publisher=43&filter_in_stock=0&limit=20&fuzzy=0&page={}"

# Selenium başlatma ayarları
chrome_options = Options()
chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştır
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-dev-shm-usage")


def fetch_books():
    """Kitapyurdu'ndan kitapları çeker ve veritabanına kaydeder."""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    page = 1
    total_books_fetched = 0
    isTest = False

    while True:
        url = BASE_URL.format(page)
        print(f"📡 Sayfa {page} taranıyor: {url}")

        driver.get(url)
        time.sleep(3)  # Sayfanın JavaScript ile tamamen yüklenmesini bekle

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ✅ Artık `product-table` gerçekten sayfada var mı kontrol edelim
        product_list = soup.find("div", {"id": "product-table"})
        if not product_list or isTest:
            print("❌ `product-table` bulunamadı, sayfa yapısı değişmiş olabilir.")
            break

        books = product_list.find_all("div", {"class": "product-cr"})
        if not books or isTest:
            print("✅ Tüm kitaplar tarandı, işlem tamamlandı.")
            break

        for book in books:
            try:
                link_element = book.find("a", {"class": "pr-img-link"})
                if link_element and "href" in link_element.attrs:
                    book_data = fetch_book_data(link_element["href"], driver)
                    if book_data:
                        print(
                            f"📖 Kitap Bulundu: ISBN: {book_data['isbn']}, Adı: {book_data['name']}, Satış: {book_data['total_sales']}"
                        )
                        update_book_sales(
                            book_data["isbn"],
                            book_data["name"],
                            book_data["total_sales"],
                        )
                        total_books_fetched += 1
                    else:
                        print("❌ Kitap verisi çekilemedi.")
                else:
                    print("❌ Link bulunamadı!")
            except Exception as e:
                print(f"❌ Kitap verisi çekerken hata oluştu: {e}")

        # page += 1
        isTest = True

    driver.quit()  # Tarayıcıyı kapat
    print(f"✅ Toplam {total_books_fetched} kitap başarıyla güncellendi.")


def fetch_book_data(url, driver):
    """Bir kitabın detaylarını çeker, ISBN’si olmayanları atlar."""
    driver.get(url)
    time.sleep(3)  # Sayfanın yüklenmesini bekle
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "pr_header__heading"}).text.strip()
        isbn_td = soup.find("td", string="ISBN:")
        isbn = (
            isbn_td.find_next("td").text.strip() if isbn_td else None
        )  # ISBN yoksa None olarak al

        # 📌 ISBN’si olmayan kitapları atlıyoruz!
        if not isbn or isbn == "N/A" or isbn.strip() == "":
            print(f"⏩ Kitap atlandı (ISBN yok): {title}")
            return None

        sales_element = soup.find("p", {"class": "purchased"})
        total_sales = (
            int(sales_element.text.split()[2].replace(".", "")) if sales_element else 0
        )

        return {"isbn": isbn, "name": title, "total_sales": total_sales}
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None
