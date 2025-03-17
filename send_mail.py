import smtplib
import os
from email.message import EmailMessage
from fastapi import HTTPException, Depends
from export_data import export_data
from auth import admin_required  # Admin kimliğini almak için
from config import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, ADMIN_EMAILS
from datetime import datetime

def send_email(admin_id: str):
    # CSV ve Excel dosyalarını oluştur
    csv_file, excel_file = export_data()

    # Eğer gönderilecek dosya yoksa hata döndür
    if not csv_file or not excel_file:
        raise HTTPException(status_code=400, detail="No data to send. Email not sent.")

    # Gönderilecek e-posta adresini belirle
    recipient_email = ADMIN_EMAILS.get(admin_id)
    if not recipient_email:
        raise HTTPException(status_code=400, detail="Admin email not found.")

    # ✅ Generate dynamic subject line and email body
    date_str = datetime.now().strftime("%d/%m/%Y")
    subject = f"Doğan Kitap Daily Sales Report - {date_str}"
    body = f"Attached are the daily book sales reports for {date_str} in CSV and Excel format."

    # E-posta oluştur
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    msg.set_content(body)

    # Dosyaları ekle
    for file_path in [csv_file, excel_file]:
        with open(file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)
            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name,
            )

    # SMTP ile gönderme işlemi
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        success_message = {"message": f"Email sent successfully to {recipient_email}!"}
        print(success_message)  # LOG ÇIKTISI EKLENDİ ✅
        return success_message

    except smtplib.SMTPAuthenticationError:
        error_message = (
            "SMTP Authentication Error. Please check your email credentials."
        )
        print(error_message)  # LOG ÇIKTISI EKLENDİ ❌
        raise HTTPException(status_code=401, detail=error_message)

    except smtplib.SMTPException as e:
        error_message = f"SMTP Error: {e}"
        print(error_message)  # LOG ÇIKTISI EKLENDİ ❌
        raise HTTPException(status_code=500, detail=error_message)
