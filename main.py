from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_all_books, get_book_by_isbn
from send_mail import send_email
from auth import admin_required
from scraper import fetch_books
from simple_forecast import compute_all_forecasts

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
    return book if book else {"error": "Buch nicht gefunden"}

@app.post("/fetch-books", dependencies=[Depends(admin_required)])
def manual_fetch_books():
    print("Buchdaten werden aktualisiert...")  # Wird beim API-Aufruf angezeigt
    fetch_books()
    print("Buchdaten wurden erfolgreich aktualisiert.")  # Abschlussmeldung
    return {"message": "Buchdaten erfolgreich aktualisiert."}

@app.post("/send-report", dependencies=[Depends(admin_required)])
def send_report(
    admin_id: str = Depends(admin_required),
):  # Autorisierter Admin-Identifier
    response = send_email(admin_id)  # Ruf die E-Mail-Versandfunktion auf und gib das Ergebnis zurück
    return response  # Rückgabe der Antwort direkt

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
        return {"error": "Buch nicht gefunden"}
    return {
        "isbn": isbn,
        "name": book.get("name"),
        "forecast_history": book.get("forecast_history", []),
    }

@app.post("/fetch-books-and-compute-forecasts")
def fetch_books_and_compute_forecasts():
    fetch_books()
    compute_all_forecasts()

