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

        # Aynı gün için bir kayıt var mı kontrol et
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
            )  # Eğer None ise 0 al
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
            # Güncellenmiş günlük satışları yaz
            books_collection.update_one(
                {"_id": isbn, "sales_history.date": today},
                {
                    "$set": {
                        "sales_history.$.total_sales": total_sales,
                        "sales_history.$.daily_sales": daily_sales,  # Günlük satışları birikimli olarak hesapla
                    },
                    "$set": update_fields,
                },
            )
        else:
            # Eğer aynı gün için giriş yoksa, yeni giriş ekle
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
        # Kitap daha önce eklenmediyse yeni kayıt oluştur
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
        print("❌ Veritabanında hiç kitap bulunamadı!")  # LOG: Eğer veri yoksa
    else:
        print(f"📚 Veritabanında {len(books)} kitap bulundu.")  # LOG: Kaç kitap var

    return books


def get_book_by_isbn(isbn):
    book = books_collection.find_one({"_id": isbn})
    return book if book else None


def save_forecast(isbn, forecast_data):
    book = books_collection.find_one({"_id": isbn})
    if not book:
        print(f"❌ Kitap bulunamadı: {isbn}")
        return

    # Tahmin yapılacak tarih: satış verisinin bir gün sonrası
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
        print(f"🔁 Tahmin zaten var, güncelleniyor: {forecast_date}")
        books_collection.update_one(
            {"_id": isbn, "forecast_history.date": forecast_date},
            {"$set": {f"forecast_history.$": forecast_data_with_date}},
        )
    else:
        print(f"🆕 Yeni tahmin ekleniyor: {forecast_date}")
        books_collection.update_one(
            {"_id": isbn},
            {"$push": {"forecast_history": forecast_data_with_date}},
        )
