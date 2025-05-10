from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from database import update_book_sales

# AKTUELLE URL für die Verlagsseite bei Kitapyurdu
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# Selenium-Optionen zum Starten des Browsers im Hintergrund
chrome_options = Options()
chrome_options.add_argument("--headless")  # Browser im Hintergrund ausführen
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-dev-shm-usage")

def fetch_books():
    """Holt Bücher von Kitapyurdu und speichert sie in die Datenbank."""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    page = 1
    total_books_fetched = 0
    isTest = False

    while True:
        url = BASE_URL.format(page)
        print(f"Seite {page} wird geladen: {url}")

        driver.get(url)
        time.sleep(5)  # Warte, bis JavaScript die Seite vollständig lädt

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Bücherliste auf der Seite extrahieren
        books = soup.find_all("div", {"class": "product-cr"})
        if not books or isTest:
            print("Alle Bücher wurden verarbeitet.")
            break

        for book in books:
            try:
                link_element = book.find("a", {"class": "pr-img-link"})
                if link_element and "href" in link_element.attrs:
                    book_data = fetch_book_data(link_element["href"], driver)
                    if book_data:
                        print(
                            f"Buch gefunden: ISBN: {book_data['isbn']}, Titel: {book_data['name']}, Verkäufe: {book_data['total_sales']}"
                        )
                        update_book_sales(
                            book_data["isbn"],
                            book_data["name"],
                            book_data["total_sales"],
                        )
                        total_books_fetched += 1
                    else:
                        print("Buchdaten konnten nicht geladen werden.")
                else:
                    print("Kein Link gefunden.")
            except Exception as e:
                print(f"Fehler beim Verarbeiten eines Buches: {e}")

        page += 1
        # isTest = True

    driver.quit()  # Browser schließen
    print(f"Insgesamt {total_books_fetched} Bücher wurden erfolgreich aktualisiert.")

def fetch_book_data(url, driver):
    """Lädt die Detailinformationen eines Buches. Bücher ohne ISBN werden übersprungen."""
    driver.get(url)
    time.sleep(3)  # Warten bis die Detailseite geladen ist
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        title = soup.find("h1", {"class": "pr_header__heading"}).text.strip()
        isbn_td = soup.find("td", string="ISBN:")
        isbn = (
            isbn_td.find_next("td").text.strip() if isbn_td else None
        )  # Falls kein ISBN vorhanden ist, auf None setzen

        # Bücher ohne ISBN überspringen
        if not isbn or isbn == "N/A" or isbn.strip() == "":
            print(f"Buch übersprungen (kein ISBN): {title}")
            return None

        sales_element = soup.find("p", {"class": "purchased"})
        total_sales = (
            int(sales_element.text.split()[2].replace(".", "")) if sales_element else 0
        )

        return {"isbn": isbn, "name": title, "total_sales": total_sales}
    except Exception as e:
        print(f"Fehler: {e}")
        return None

