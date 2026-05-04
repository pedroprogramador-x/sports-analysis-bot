import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.daily_pick_service import find_daily_pick, find_daily_acca
from app.services.telegram_service import (
    send_daily_pick_notification,
    send_daily_acca_notification
)


def run_daily_pick():
    pick = asyncio.run(find_daily_pick())
    asyncio.run(send_daily_pick_notification(pick))

    acca = asyncio.run(find_daily_acca())
    asyncio.run(send_daily_acca_notification(acca))


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Fortaleza")
    scheduler.add_job(run_daily_pick, "cron", hour=9, minute=0)
    scheduler.start()
    return scheduler