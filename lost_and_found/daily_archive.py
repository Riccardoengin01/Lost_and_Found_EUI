import time
import schedule
from .utils import archivia_scaduti


def job():
    archivia_scaduti()


def start_scheduler():
    schedule.every().day.at("00:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
