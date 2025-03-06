# from apscheduler.schedulers.background import BackgroundScheduler
# from scraper import fetch_books
# import time

# scheduler = BackgroundScheduler()
# scheduler.add_job(
#     fetch_books, "cron", hour=3, minute=0
# )  # Her gün saat 03:00'te çalıştır

# scheduler.start()
# print("✅ Otomatik veri güncelleme başladı!")

# try:
#     while True:
#         time.sleep(1)
# except (KeyboardInterrupt, SystemExit):
#     scheduler.shutdown()

from apscheduler.schedulers.background import BackgroundScheduler
from scraper import fetch_books
import time

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_books, "interval", minutes=2)  # 2 dakikada bir çalıştır

scheduler.start()
print("✅ Otomatik veri güncelleme başladı! (Her 2 dakikada bir çalışıyor)")

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
