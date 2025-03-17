from fastapi import FastAPI, Depends
from database import get_all_books, get_book_by_isbn
from send_mail import send_email
from auth import admin_required
from scraper import fetch_books


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

