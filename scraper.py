import requests
from bs4 import BeautifulSoup
from database import update_book_sales
import time

# GÜNCEL URL
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# Tarayıcıyı taklit eden bir User-Agent belirle
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_books():
    """Kitapyurdu'ndan kitapları çeker ve veritabanına kaydeder."""
    page = 1
    total_books_fetched = 0

    while True:
        url = BASE_URL.format(page)
        print(f"📡 Sayfa {page} taranıyor: {url}")

        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Sayfa yüklenirken hata oluştu: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("div", {"class": "product-cr"})
        if not books:
            print("✅ Tüm kitaplar tarandı, işlem tamamlandı.")
            break

        for book in books:
            try:
                link_element = book.find("a", {"class": "pr-img-link"})
                if link_element and "href" in link_element.attrs:
                    book_url = link_element["href"]
                    book_data = fetch_book_data(book_url)

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

        page += 1
        time.sleep(1)  # Sunucuyu yormamak için 1 saniye bekleyelim

    print(f"✅ Toplam {total_books_fetched} kitap başarıyla güncellendi.")


def fetch_book_data(book_url):
    """Bir kitabın detaylarını çeker, ISBN’si olmayanları atlar."""
    response = requests.get(book_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Kitap sayfası yüklenirken hata oluştu: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

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
