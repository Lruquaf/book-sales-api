from pymongo import MongoClient
from datetime import datetime, timezone
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
books_collection = db["books"]


def update_book_sales(isbn, name, total_sales):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    book = books_collection.find_one({"_id": isbn})

    if book:
        previous_sales = book.get("total_sales", 0)
        daily_sales = (
            total_sales - previous_sales if total_sales >= previous_sales else None
        )

        books_collection.update_one(
            {"_id": isbn},
            {
                "$set": {
                    "name": name,
                    "total_sales": total_sales,
                    "last_updated": datetime.now(timezone.utc),
                },
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
