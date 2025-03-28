from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_all_books, get_book_by_isbn
from send_mail import send_email
from auth import admin_required
from scraper import fetch_books
from simple_forecast import (
    compute_all_forecasts,
    compute_forecast_by_isbn,
    # recover_forecast
)


# # **📌 Lifespan Event Handler Tanımlama**
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("🚀 API başlatılıyor, scheduler devreye giriyor...")

#     # **Scheduler'ı Başlat**
#     scheduler = BackgroundScheduler(timezone="Europe/Istanbul")  # Türkiye Saati (UTC+3)
#     scheduler.add_job(
#         fetch_books, "cron", hour=21, minute=0
#     )  # **Her gün saat 21:00'de çalışacak**
#     scheduler.start()
#     print("✅ Scheduler başlatıldı! (Her gün saat 21:00'de çalışacak)")

#     yield  # API çalışırken burada bekleyecek

#     # **API Kapanınca Scheduler'ı Durdur**
#     scheduler.shutdown()
#     print("🛑 Scheduler durduruldu, API kapanıyor.")


# **📌 FastAPI Uygulaması**
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Book Sales API"}


@app.get("/books")
def get_books():
    return get_all_books()


@app.get("/books/{isbn}")
def get_book(isbn: str):
    book = get_book_by_isbn(isbn)
    return book if book else {"error": "Book not found"}


@app.post("/fetch-books", dependencies=[Depends(admin_required)])
def manual_fetch_books():
    print("📡 Kitap verileri güncelleniyor...")  # LOG: API çağrıldığında göster
    fetch_books()
    print("✅ Kitap verileri başarıyla güncellendi!")  # LOG: İşlem tamamlandı mesajı
    return {"message": "Books data updated successfully!"}


@app.post("/send-report", dependencies=[Depends(admin_required)])
def send_report(
    admin_id: str = Depends(admin_required),
):  # Yetkilendirilen admin kimliği
    response = send_email(admin_id)  # Mail gönderme fonksiyonunu çağır ve sonucu al
    return response  # Doğrudan dönüş değerini return et


# @app.get("/forecasts")
# def get_all_forecasts():
#     return compute_all_forecasts()


# @app.get("/forecasts/{isbn}/test")
# def get_forecast_by_isbn(isbn: str):
#     return compute_forecast_by_isbn(isbn)

# @app.post("/forecasts/recover")
# def recover():
#     return recover_forecast()


@app.post("/forecasts/compute")
def compute_and_save_forecasts():
    return compute_all_forecasts()


@app.get("/forecasts")
def get_all_forecasts_from_db():
    from database import books_collection

    books = books_collection.find({}, {"_id": 1, "name": 1, "forecast_history": 1})
    return list(books)


@app.get("/forecasts/{isbn}")
def get_forecast_by_book(isbn: str):
    book = get_book_by_isbn(isbn)
    if not book:
        return {"error": "Book not found"}
    return {
        "isbn": isbn,
        "name": book.get("name"),
        "forecast_history": book.get("forecast_history", []),
    }


@app.post("/fetch-books-and-compute-forecasts")
def fetch_books_and_compute_forecasts():
    fetch_books()
    compute_all_forecasts()
