from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

# MongoDB bağlantısı
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
books = db["books"]

wrong_date = "2025-03-29"
correct_date = "2025-03-28"

# Kaç kayıt güncellendiğini takip etmek için sayaç
updated_count = 0

# forecast_history'de hatalı tarihi içeren tüm kitapları bul
for book in books.find({"forecast_history.date": wrong_date}):
    forecast_history = book.get("forecast_history", [])
    new_history = []

    for entry in forecast_history:
        if entry["date"] == wrong_date:
            print(f"🔧 Düzeltiliyor: {book['_id']} - {entry}")
            entry["date"] = correct_date
            updated_count += 1
        new_history.append(entry)

    # Veriyi güncelle
    books.update_one({"_id": book["_id"]}, {"$set": {"forecast_history": new_history}})

print(f"✅ Toplam {updated_count} adet forecast tarihi başarıyla düzeltildi.")
