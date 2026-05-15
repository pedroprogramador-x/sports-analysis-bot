import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.bsd_service import get_todays_events
from app.services.daily_pick_service import (
    find_conservative_pick,
    find_daily_pick,
    find_daily_acca,
)
from app.services.telegram_service import (
    send_conservative_pick_notification,
    send_daily_pick_notification,
    send_daily_acca_notification,
)

logger = logging.getLogger(__name__)


async def _run_all_picks():
    events = await get_todays_events()

    conservative, pick, acca = await asyncio.gather(
        find_conservative_pick(events),
        find_daily_pick(events),
        find_daily_acca(events),
    )

    await send_conservative_pick_notification(conservative)
    await send_daily_pick_notification(pick)
    await send_daily_acca_notification(acca)


def run_daily_pick():
    try:
        asyncio.run(_run_all_picks())
    except Exception:
        logger.exception("Erro ao executar picks diários")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Fortaleza")
    scheduler.add_job(run_daily_pick, "cron", hour=9, minute=0)
    scheduler.start()
    return scheduler
