import requests
from bs4 import BeautifulSoup
from database import update_book_sales
import time

# AKTUELLE URL für die Verlagsseite bei Kitapyurdu
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# User-Agent definieren, um den Browser zu imitieren
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_books():
    """Holt Bücher von Kitapyurdu und speichert sie in die Datenbank."""
    page = 1
    total_books_fetched = 0

    while True:
        url = BASE_URL.format(page)
        print(f"Seite {page} wird geladen: {url}")

        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Fehler beim Laden der Seite: Status {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Alle Bücher auf der Seite finden
        books = soup.find_all("div", {"class": "product-cr"})
        if not books:
            print("Alle Bücher wurden verarbeitet.")
            break

        for book in books:
            try:
                link_element = book.find("a", {"class": "pr-img-link"})
                if link_element and "href" in link_element.attrs:
                    book_url = link_element["href"]
                    book_data = fetch_book_data(book_url)

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
                    print("Link nicht gefunden.")
            except Exception as e:
                print(f"Fehler beim Verarbeiten eines Buches: {e}")

        page += 1
        time.sleep(1)  # 1 Sekunde warten, um den Server nicht zu überlasten

    print(f"Insgesamt {total_books_fetched} Bücher wurden erfolgreich aktualisiert.")

def fetch_book_data(book_url):
    """Lädt die Detailinformationen eines Buches. Bücher ohne ISBN werden übersprungen."""
    response = requests.get(book_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Fehler beim Laden der Buchseite: Status {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

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

