from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_all_books, get_book_by_isbn
from send_mail import send_email
from auth import admin_required
from scraper import fetch_books


# **📌 Lifespan Event Handler Tanımlama**
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 API başlatılıyor, scheduler devreye giriyor...")

    # **Scheduler'ı Başlat**
    scheduler = BackgroundScheduler(timezone="Europe/Istanbul")  # Türkiye Saati (UTC+3)
    scheduler.add_job(
        fetch_books, "cron", hour=21, minute=0
    )  # **Her gün saat 21:00'de çalışacak**
    scheduler.start()
    print("✅ Scheduler başlatıldı! (Her gün saat 21:00'de çalışacak)")

    yield  # API çalışırken burada bekleyecek

    # **API Kapanınca Scheduler'ı Durdur**
    scheduler.shutdown()
    print("🛑 Scheduler durduruldu, API kapanıyor.")


# **📌 FastAPI Uygulaması**
app = FastAPI(lifespan=lifespan)


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
