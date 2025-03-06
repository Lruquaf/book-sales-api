import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# MongoDB Ayarları
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Email Ayarları
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# Admin Kullanıcıları (id:token)
ADMIN_USERS = {
    user.split(":")[0]: user.split(":")[1]
    for user in os.getenv("ADMIN_USERS", "").split(",")
    if ":" in user
}

# Admin E-posta Adresleri (id:email)
ADMIN_EMAILS = {
    user.split(":")[0]: user.split(":")[1]
    for user in os.getenv("ADMIN_EMAILS", "").split(",")
    if ":" in user
}
