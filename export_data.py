import pandas as pd
import os
from database import get_all_books
from datetime import datetime

# Kaydedilecek klasör
EXPORT_DIR = "book_sales_files"

# Eğer klasör yoksa oluştur
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_data():
    books = get_all_books()

    if not books:
        return None, None

    data = []
    for book in books:
        sales_dict = {
            entry["date"]: entry["daily_sales"]
            for entry in book.get("sales_history", [])
        }
        row = {
            "ISBN": book["_id"],
            "Title": book["name"],
            "Total Sales": book["total_sales"],
        }
        row.update(sales_dict)
        data.append(row)

    df = pd.DataFrame(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(EXPORT_DIR, f"book_sales_{timestamp}.csv")
    excel_filename = os.path.join(EXPORT_DIR, f"book_sales_{timestamp}.xlsx")

    df.to_csv(csv_filename, index=False)
    df.to_excel(excel_filename, index=False)

    return csv_filename, excel_filename
