import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.daily_pick_service import find_daily_pick
from app.services.telegram_service import send_daily_pick_notification


def run_daily_pick():
    pick = asyncio.run(find_daily_pick())
    asyncio.run(send_daily_pick_notification(pick))


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Maceio")
    scheduler.add_job(run_daily_pick, "cron", hour=9, minute=0)
    scheduler.start()
    return scheduler