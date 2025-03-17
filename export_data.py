import pandas as pd
import os
from database import get_all_books
from datetime import datetime

EXPORT_DIR = "book_sales_files"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_data():
    books = get_all_books()
    if not books:
        return None, None

    data = []
    for book in books:
        row = {
            "ISBN": book["_id"],
            "tarih": book.get("date", None),  # ✅ Include date
            "url": book.get("url", None),
            "book_name": book.get("name", None),
            "writer": book.get("author", None),
            "purchased_count": book.get("total_sales", None),
            "stock": book.get("stock", None),
            "price": book.get("price", None)
        }
        data.append(row)

    # ✅ Ensure correct column order
    df = pd.DataFrame(data, columns=[
        "ISBN", "tarih", "url", "book_name", "writer", "purchased_count", "stock", "price"
    ])

    # ✅ File naming and utf-8 encoding
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(EXPORT_DIR, f"g1_{timestamp}.csv")
    excel_filename = os.path.join(EXPORT_DIR, f"g1_{timestamp}.xlsx")

    df.to_csv(csv_filename, index=False, encoding="utf-8")
    df.to_excel(excel_filename, index=False)

    return csv_filename, excel_filename
