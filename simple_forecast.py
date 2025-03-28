from database import get_all_books, get_book_by_isbn


from database import save_forecast


def compute_all_forecasts():
    books = get_all_books()
    results = []

    print(f"🔍 {len(books)} kitap bulundu. Tahminler hesaplanıyor...\n")

    for book in books:
        isbn = book.get("_id", "UNKNOWN")
        name = book.get("name", "UNKNOWN")
        sales_history = book.get("sales_history", [])

        print(f"📘 [{isbn}] {name} - {len(sales_history)} günlük satış verisi bulundu.")

        if not sales_history:
            print(f"⚠️  Veri yok, tahmin atlandı.\n")
            continue

        forecasts = compute_forecasts(sales_history)
        save_forecast(isbn, forecasts)
        results.append({"isbn": isbn, "name": name, "forecasts": forecasts})
        print(f"✅ Tahminler: {forecasts}\n")

    print("🎯 Tüm kitaplar için tahmin işlemi tamamlandı.\n")
    return results


def compute_forecast_by_isbn(isbn):
    print(f"🔎 ISBN ile sorgulama başlatıldı: {isbn}")
    book = get_book_by_isbn(isbn)

    if not book:
        print("❌ Kitap bulunamadı!")
        return {"error": "Book not found"}

    name = book.get("name", "UNKNOWN")
    sales_history = book.get("sales_history", [])

    print(f"📗 {name} kitabı bulundu. {len(sales_history)} satış verisi var.")

    if not sales_history:
        print("⚠️  Satış verisi yok, tahmin yapılamıyor.")
        return {"error": "No sales history available for this book"}

    forecasts = compute_forecasts(sales_history)

    print(f"✅ Tahminler: {forecasts}")
    return {"isbn": isbn, "name": name, "forecasts": forecasts}


def weighted_moving_average(sales, weights):
    if len(sales) < len(weights):
        print(f"⚠️  Yetersiz veri: {len(sales)} gün var, {len(weights)} gerekiyor.")
        return None
    recent_sales = sales[-len(weights) :]
    wma = round(sum(w * s for w, s in zip(weights, recent_sales)), 2)
    return wma


def compute_forecasts(sales_history):
    daily_sales = [
        entry.get("daily_sales", 0) or 0
        for entry in sorted(sales_history, key=lambda x: x["date"])
    ]

    print(f"🧮 Günlük satışlar: {daily_sales[-15:]}")  # Son 15 günü göster

    result = {}

    weights_3 = [0.2, 0.3, 0.5]
    weights_7 = [0.05, 0.07, 0.1, 0.13, 0.15, 0.2, 0.3]
    weights_14 = [i / sum(range(1, 15)) for i in range(1, 15)]  # normalize [1...14]

    result["wma_3"] = weighted_moving_average(daily_sales, weights_3)
    result["wma_7"] = weighted_moving_average(daily_sales, weights_7)
    result["wma_14"] = weighted_moving_average(daily_sales, weights_14)

    valid_values = [
        v for v in [result["wma_3"], result["wma_7"], result["wma_14"]] if v is not None
    ]
    result["combined_forecast"] = (
        round(sum(valid_values) / len(valid_values), 2) if valid_values else None
    )

    return result


# def compute_forecasts_test(sales_history):
#     daily_sales = [
#         entry.get("daily_sales", 0) or 0
#         for entry in sorted(sales_history, key=lambda x: x["date"])
#     ]

#     print(f"🧮 [TEST] Günlük satışlar: {daily_sales[-15:]}")

#     result = {}

#     # WMA ağırlıkları
#     weights_3 = [0.2, 0.3, 0.5]
#     weights_7 = [0.05, 0.07, 0.1, 0.13, 0.15, 0.2, 0.3]
#     weights_14 = [i / sum(range(1, 15)) for i in range(1, 15)]

#     # Tahminler
#     wma_3 = weighted_moving_average(daily_sales, weights_3)
#     wma_7 = weighted_moving_average(daily_sales, weights_7)
#     wma_14 = weighted_moving_average(daily_sales, weights_14)

#     result["wma_3"] = wma_3
#     result["wma_7"] = wma_7
#     result["wma_14"] = wma_14

#     # 🎯 Alternatif combined: son gün etkisini dengeleyen formül
#     if all(v is not None for v in [wma_3, wma_7, wma_14]):
#         combined = 0.25 * wma_3 + 0.35 * wma_7 + 0.40 * wma_14
#         result["combined_forecast"] = round(combined, 2)
#     else:
#         result["combined_forecast"] = None

#     print(f"📊 [TEST] Alternatif Combined Forecast: {result['combined_forecast']}")
#     return result


# from datetime import datetime, timedelta


# def recover_forecast():
#     books = get_all_books()

#     print(f"♻️ [RECOVER] {len(books)} kitap için tahmin toparlama başlatıldı...\n")

#     for book in books:
#         isbn = book.get("_id", "UNKNOWN")
#         name = book.get("name", "UNKNOWN")
#         sales_history = book.get("sales_history", [])

#         if len(sales_history) < 2:
#             print(f"⏩ [{isbn}] {name} - Yetersiz veri, atlandı.")
#             continue

#         # Tarihe göre sırala
#         sorted_history = sorted(sales_history, key=lambda x: x["date"])
#         truncated_sales = sorted_history[:-1]  # En son gün hariç

#         # Tahmin gününü belirle: son gün + 1
#         last_date = datetime.strptime(sorted_history[-1]["date"], "%Y-%m-%d")
#         forecast_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

#         forecast = compute_forecasts_for_recovery(truncated_sales)
#         if any(v is not None for v in forecast.values()):
#             forecast["date"] = forecast_date
#             save_forecast(isbn, forecast)
#             print(f"✅ [{isbn}] {name} - {forecast_date} için tahmin: {forecast}")
#         else:
#             print(f"⚠️ [{isbn}] {name} - Tahmin oluşturulamadı.")


# def compute_forecasts_for_recovery(sales_history):
#     """Son günü dahil etmeden forecast hesaplar."""
#     daily_sales = [entry.get("daily_sales", 0) or 0 for entry in sales_history]

#     result = {}

#     weights_3 = [0.2, 0.3, 0.5]
#     weights_7 = [0.05, 0.07, 0.1, 0.13, 0.15, 0.2, 0.3]
#     weights_14 = [i / sum(range(1, 15)) for i in range(1, 15)]

#     result["wma_3"] = weighted_moving_average(daily_sales, weights_3)
#     result["wma_7"] = weighted_moving_average(daily_sales, weights_7)
#     result["wma_14"] = weighted_moving_average(daily_sales, weights_14)

#     # Alternatif combined ağırlıklar
#     if all(v is not None for v in [result["wma_3"], result["wma_7"], result["wma_14"]]):
#         result["combined_forecast"] = round(
#             0.25 * result["wma_3"] + 0.35 * result["wma_7"] + 0.40 * result["wma_14"], 2
#         )
#     else:
#         result["combined_forecast"] = None

#     return result
