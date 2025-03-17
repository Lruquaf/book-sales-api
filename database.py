from pymongo import MongoClient
from datetime import datetime, timezone
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
books_collection = db["books"]

def update_book_sales(isbn, name, total_sales=None, author=None, price=None, stock=None, url=None, date=None):
    # ✅ Default to today's date if not provided
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    book = books_collection.find_one({"_id": isbn})

    if book:
        previous_total_sales = book.get("total_sales", 0) or 0

        # ✅ Handle existing sales entry
        existing_sales_entry = next(
            (entry for entry in book.get("sales_history", []) if entry["date"] == date),
            None,
        )

        if existing_sales_entry:
            last_recorded_total_sales = existing_sales_entry["total_sales"] or 0
            previous_daily_sales = existing_sales_entry["daily_sales"] or 0
            daily_sales = (total_sales or 0) - last_recorded_total_sales + previous_daily_sales
        else:
            daily_sales = (total_sales or 0) - previous_total_sales if total_sales and total_sales >= previous_total_sales else None

        update_fields = {
            "name": name,
            "author": author,          # ✅ Allow None
            "price": price,            # ✅ Allow None
            "stock": stock,            # ✅ Allow None
            "url": url,                # ✅ Allow None
            "total_sales": total_sales or 0,  # ✅ Default to 0 if None
            "date": date,              # ✅ Fixed date handling
            "last_updated": datetime.now(timezone.utc),
        }

        if existing_sales_entry:
            # ✅ Update existing entry
            books_collection.update_one(
                {"_id": isbn, "sales_history.date": date},
                {
                    "$set": {
                        "sales_history.$.total_sales": total_sales or 0,
                        "sales_history.$.daily_sales": daily_sales or 0,
                        **update_fields,  # ✅ Include all fields in update
                    }
                }
            )
        else:
            # ✅ Create new sales history entry if no entry for today
            books_collection.update_one(
                {"_id": isbn},
                {
                    "$set": update_fields,
                    "$push": {
                        "sales_history": {
                            "date": date,
                            "daily_sales": daily_sales,
                            "total_sales": total_sales or 0,
                        }
                    },
                },
            )
    else:
        # ✅ Insert new book entry if it doesn't exist
        books_collection.insert_one(
            {
                "_id": isbn,
                "name": name,
                "author": author,
                "price": price,
                "stock": stock,
                "url": url,
                "total_sales": total_sales or 0,
                "date": date,  # ✅ Fixed date handling
                "sales_history": [
                    {"date": date, "daily_sales": None, "total_sales": total_sales or 0}
                ],
                "last_updated": datetime.now(timezone.utc),
            }
        )

def get_all_books():
    books = list(
        books_collection.find(
            {}, 
            {
                "_id": 1,
                "name": 1,
                "author": 1,
                "price": 1,
                "stock": 1,
                "url": 1,
                "total_sales": 1,
                "date": 1,  # ✅ Include date in query
                "sales_history": 1
            }
        )
    )

    return books

def get_book_by_isbn(isbn):
    book = books_collection.find_one({"_id": isbn})
    return book if book else None