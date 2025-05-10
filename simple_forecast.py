from database import get_all_books, get_book_by_isbn
from database import save_forecast

def compute_all_forecasts():
    books = get_all_books()
    results = []

    print(f"{len(books)} Bücher gefunden. Prognosen werden berechnet...\n")

    for book in books:
        isbn = book.get("_id", "UNKNOWN")
        name = book.get("name", "UNKNOWN")
        sales_history = book.get("sales_history", [])

        print(f"[{isbn}] {name} - {len(sales_history)} Verkaufseinträge gefunden.")

        if not sales_history:
            print("Keine Daten vorhanden, Prognose übersprungen.\n")
            continue

        forecasts = compute_forecasts(sales_history)
        save_forecast(isbn, forecasts)
        results.append({"isbn": isbn, "name": name, "forecasts": forecasts})
        print(f"Prognoseergebnisse: {forecasts}\n")

    print("Alle Prognosen wurden berechnet.\n")
    return results

def compute_forecast_by_isbn(isbn):
    print(f"Prognose wird gestartet für ISBN: {isbn}")
    book = get_book_by_isbn(isbn)

    if not book:
        print("Buch nicht gefunden.")
        return {"error": "Book not found"}

    name = book.get("name", "UNKNOWN")
    sales_history = book.get("sales_history", [])

    print(f"{name} gefunden. Anzahl Verkaufsdaten: {len(sales_history)}")

    if not sales_history:
        print("Keine Verkaufsdaten vorhanden. Prognose nicht möglich.")
        return {"error": "No sales history available for this book"}

    forecasts = compute_forecasts(sales_history)

    print(f"Prognoseergebnisse: {forecasts}")
    return {"isbn": isbn, "name": name, "forecasts": forecasts}

def weighted_moving_average(sales, weights):
    # Prüfen, ob genügend Daten vorhanden sind
    if len(sales) < len(weights):
        print(f"Nicht genügend Daten: {len(sales)} vorhanden, {len(weights)} benötigt.")
        return None

    recent_sales = sales[-len(weights):]
    wma = round(sum(w * s for w, s in zip(weights, recent_sales)), 2)
    return wma

def compute_forecasts(sales_history):
    # Tagesverkäufe extrahieren und nach Datum sortieren
    daily_sales = [
        entry.get("daily_sales", 0) or 0
        for entry in sorted(sales_history, key=lambda x: x["date"])
    ]

    print(f"Tagesverkäufe (letzte 15 Tage): {daily_sales[-15:]}")

    result = {}

    # Gewichtungen für verschiedene Zeitfenster
    weights_3 = [0.2, 0.3, 0.5]
    weights_7 = [0.05, 0.07, 0.1, 0.13, 0.15, 0.2, 0.3]
    weights_14 = [i / sum(range(1, 15)) for i in range(1, 15)]  # Normalisierte Gewichte von 1 bis 14

    # Einzelne gewichtete Durchschnitte berechnen
    result["wma_3"] = weighted_moving_average(daily_sales, weights_3)
    result["wma_7"] = weighted_moving_average(daily_sales, weights_7)
    result["wma_14"] = weighted_moving_average(daily_sales, weights_14)

    # Kombinierte Prognose als Mittelwert aller gültigen Werte
    valid_values = [
        v for v in [result["wma_3"], result["wma_7"], result["wma_14"]] if v is not None
    ]
    result["combined_forecast"] = (
        round(sum(valid_values) / len(valid_values), 2) if valid_values else None
    )

    return result

