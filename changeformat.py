import requests
from bs4 import BeautifulSoup
import time
import csv
import os
from datetime import datetime
import chardet
import unicodedata

# Basis-URL für das Abrufen der Buchlisten
BASE_URL = "https://www.kitapyurdu.com/index.php?route=product/publisher_products/all&sort=pd.name&order=ASC&publisher_id=43&filter_in_stock=1&limit=100&page={}"

# Name der CSV-Datei mit aktuellem Datum
CSV_FILE = f"g1_{datetime.now().strftime('%Y%m%d')}.csv"

# Header, um nicht als Bot erkannt zu werden
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, wie Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Zeichenersetzungstabelle für falsch dekodierte türkische Zeichen
# Behebt fehlerhafte Zeichen wie thailändische Symbole oder Kodierungsreste
# Entfernt unerwünschte Symbole
CHARACTER_MAP = {
    '√º': 'ü', '√ß': 'ç',
    '√ú': 'Ü',
    '≈û': 'Ş', '≈ü': 'ş',
    'Ã‡': 'Ç', 'Ã§': 'ç',
    'Ä°': 'İ', 'Ä±': 'ı',
    'ÅŸ': 'ş', 'ÅŞ': 'Ş',
    'ÄŸ': 'ğ', 'Äž': 'Ğ',
    'Ã¼': 'ü', 'ÃÜ': 'Ü',
    'Ã¶': 'ö', 'ÃÖ': 'Ö',
    'Ã¢': 'â', 'ÃÂ': 'Â',
    'Ãª': 'ê', 'ÃÊ': 'Ê',
    'Ãá': 'á', 'ÃÁ': 'Á',
    'Ã©': 'é', 'ÃÉ': 'É',
    'Ãè': 'è', 'ÃÈ': 'È',
    'Ãë': 'ë', 'ÃË': 'Ë',
    'Ãô': 'ô', 'ÃÔ': 'Ô',
    'Ãø': 'ø', 'ÃØ': 'Ø',
    'Ã£': 'ã', 'ÃÃ': 'Ã',
    'Ãõ': 'õ', 'ÃÕ': 'Õ',
    'â€™': "'", 'â€˜': "'",
    'ÃŸ': 'ß', 'â€“': '-',
    'â€”': '—', 'â€œ': '"',
    'â€': '"', 'â€¦': '…',
    'Ã': 'ı', 'Ä': 'İ',
    'Å': 'Ş', 'Ã¿': 'ÿ',
    'ก': 'ı', 'ษ': 'Ş', '™': '',  
    '¶': '', '§': '',  
}

# Funktion zum Bereinigen und Dekodieren fehlerhafter Zeichen
def fix_turkish_characters(text):
    if isinstance(text, str):
        try:
            # Schritt 1: Doppelte Dekodierung (ISO-8859-9 → UTF-8)
            text = text.encode('ISO-8859-9').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        
        # Schritt 2: Zeichenersetzung gemäß CHARACTER_MAP
        for wrong_char, correct_char in CHARACTER_MAP.items():
            text = text.replace(wrong_char, correct_char)

        # Schritt 3: Unicode-Normalisierung zur Bereinigung von Kombinationszeichen
        text = unicodedata.normalize("NFC", text)

    return text

# Speichert Buchdaten in eine CSV-Datei
def save_to_csv(data, filename=CSV_FILE):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Schreibe Header nur, wenn die Datei neu erstellt wurde
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

# Holt die Buchliste von einer bestimmten Seite (erste Ebene)
def fetch_book_list(page):
    url = BASE_URL.format(page)
    print(f"📡 Seite {page} wird geladen: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        # Kodierung mit chardet erkennen
        encoding = chardet.detect(response.content)["encoding"]
        html = response.content.decode(encoding or "utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"❌ Anfrage fehlgeschlagen: {e}")
        return []

    books = soup.find_all("div", {"class": "product-cr"})
    if not books:
        print(f"⚠️ Keine Bücher auf Seite {page} gefunden")
    return books

# Holt detaillierte Buchinformationen von der Buchdetailseite (zweite Ebene)
def fetch_book_data(url):
    """Holt die Detailinformationen eines einzelnen Buchs; überspringt Bücher ohne ISBN."""
    if not url.startswith("http"):
        url = "https://www.kitapyurdu.com" + url
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Anfrage fehlgeschlagen: {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    try:
        title = soup.find("h1", {"class": "pr_header__heading"}).text.strip()
        isbn_td = soup.find("td", string="ISBN:")
        isbn = isbn_td.find_next("td").text.strip() if isbn_td else None

        if not isbn:
            print(f"⏩ Buch übersprungen (Keine ISBN): {title}")
            return None
        
        # Extrahiere Verkaufszahlen
        sales_element = soup.find("p", {"class": "purchased"})
        total_sales = None
        if sales_element:
            try:
                total_sales = int(sales_element.text.split()[2].replace(".", ""))
            except (ValueError, IndexError):
                total_sales = None
                
        # Extrahiere Autor
        author_element = soup.find("a", {"class": "pr_producers__link"})
        author = fix_turkish_characters(author_element.text.strip()) if author_element else None
        
        # Extrahiere Preis
        price_meta = soup.find("meta", {"itemprop": "price"})
        price = float(price_meta.get("content")) if price_meta else None

        # Extrahiere Lagerbestand
        stock_element = soup.find("span", {"class": "stock-info"})
        stock = None
        if stock_element:
            stock_text = stock_element.text.strip()
            if "10+" in stock_text:
                stock = 11
            elif "Stokta" in stock_text:
                stock = int(stock_text.split()[1]) if stock_text.split()[1].isdigit() else None

        return {
            "isbn": isbn,
            "name": fix_turkish_characters(title),
            "author": author,
            "price": price,
            "stock": stock,
            "total_sales": total_sales,
            "url": url,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    
    except Exception as e:
        print(f"❌ Fehler beim Parsen der Buchdetails: {e}")
        return None

# HAUPTFUNKTION
def main():
    """Hauptfunktion zum Scrapen der Bücher und Speichern in eine CSV-Datei."""
    page = 1
    total_books = 0
    
    while True:
        books = fetch_book_list(page)
        if not books:
            break
        
        for book in books:
            link = book.find("a", {"class": "pr-img-link"})
            if link and "href" in link.attrs:
                book_url = link["href"]
                book_data = fetch_book_data(book_url)
                if book_data:
                    print(f"✅ Buch gefunden: {book_data['name']}")
                    save_to_csv(book_data)
                    total_books += 1
            else:
                print("❌ Link nicht gefunden!")

        page += 1
        time.sleep(2) # Kurze Pause zur Vermeidung von Sperrung durch die Webseite
    
    print(f"✅ {total_books} Bücher wurden erfolgreich gespeichert.")

if __name__ == "__main__":
    main()





