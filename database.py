from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
books_collection = db["books"]

def update_book_sales(isbn, name, total_sales):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    book = books_collection.find_one({"_id": isbn})

    if book:
        previous_total_sales = book.get("total_sales", 0)

        # Prüfen, ob es bereits einen Eintrag für das heutige Datum gibt
        existing_sales_entry = next(
            (
                entry
                for entry in book.get("sales_history", [])
                if entry["date"] == today
            ),
            None,
        )

        if existing_sales_entry:
            last_recorded_total_sales = existing_sales_entry["total_sales"]
            previous_daily_sales = (
                existing_sales_entry["daily_sales"] or 0
            )  # Falls None, als 0 behandeln
            daily_sales = (
                total_sales - last_recorded_total_sales
            ) + previous_daily_sales
        else:
            daily_sales = (
                total_sales - previous_total_sales
                if total_sales >= previous_total_sales
                else None
            )

        update_fields = {
            "name": name,
            "total_sales": total_sales,
            "last_updated": datetime.now(timezone.utc),
        }

        if existing_sales_entry:
            # Aktualisierung der täglichen Verkaufszahlen
            books_collection.update_one(
                {"_id": isbn, "sales_history.date": today},
                {
                    "$set": {
                        "sales_history.$.total_sales": total_sales,
                        "sales_history.$.daily_sales": daily_sales,
                    },
                    "$set": update_fields,
                },
            )
        else:
            # Neuer Eintrag für den heutigen Tag hinzufügen
            books_collection.update_one(
                {"_id": isbn},
                {
                    "$set": update_fields,
                    "$push": {
                        "sales_history": {
                            "date": today,
                            "daily_sales": daily_sales,
                            "total_sales": total_sales,
                        }
                    },
                },
            )

    else:
        # Neues Buchdokument erstellen, wenn es noch nicht vorhanden ist
        books_collection.insert_one(
            {
                "_id": isbn,
                "name": name,
                "total_sales": total_sales,
                "sales_history": [
                    {"date": today, "daily_sales": None, "total_sales": total_sales}
                ],
                "last_updated": datetime.now(timezone.utc),
            }
        )

def get_all_books():
    books = list(
        books_collection.find(
            {}, {"_id": 1, "name": 1, "total_sales": 1, "sales_history": 1}
        )
    )

    if not books:
        print("Es wurden keine Bücher in der Datenbank gefunden.")
    else:
        print(f"Insgesamt {len(books)} Bücher in der Datenbank gefunden.")

    return books

def get_book_by_isbn(isbn):
    book = books_collection.find_one({"_id": isbn})
    return book if book else None

def save_forecast(isbn, forecast_data):
    book = books_collection.find_one({"_id": isbn})
    if not book:
        print(f"Buch mit ISBN {isbn} nicht gefunden.")
        return

    # Prognosedatum ist der Tag nach dem letzten Verkaufsdatum
    latest_date = sorted(book.get("sales_history", []), key=lambda x: x["date"])[-1][
        "date"
    ]
    forecast_date = (
        datetime.strptime(latest_date, "%Y-%m-%d") + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    existing_entry = next(
        (f for f in book.get("forecast_history", []) if f["date"] == forecast_date),
        None,
    )

    forecast_data_with_date = {"date": forecast_date, **forecast_data}

    if existing_entry:
        print(f"Prognose für {forecast_date} bereits vorhanden. Aktualisierung wird durchgeführt.")
        books_collection.update_one(
            {"_id": isbn, "forecast_history.date": forecast_date},
            {"$set": {f"forecast_history.$": forecast_data_with_date}},
        )
    else:
        print(f"Neue Prognose wird gespeichert für {forecast_date}.")
        books_collection.update_one(
            {"_id": isbn},
            {"$push": {"forecast_history": forecast_data_with_date}},
        )

