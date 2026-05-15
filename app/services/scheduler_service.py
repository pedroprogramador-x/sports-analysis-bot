import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.bsd_service import get_todays_events
from app.services.daily_pick_service import (
    find_conservative_pick,
    find_daily_pick,
    find_daily_acca,
    save_picks_to_db,
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
    save_picks_to_db(conservative, pick, acca)


def run_daily_pick():
    try:
        asyncio.run(_run_all_picks())
    except Exception:
        logger.exception("Erro ao executar picks diários")


def run_result_check():
    from app.services.result_checker_service import update_pending_results
    try:
        summary = asyncio.run(update_pending_results())
        logger.info("Resultados atualizados: %s", summary)
    except Exception:
        logger.exception("Erro ao verificar resultados pendentes")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Fortaleza")
    scheduler.add_job(run_daily_pick,    "cron", hour=9,  minute=0)
    scheduler.add_job(run_result_check,  "cron", hour=23, minute=0)
    scheduler.start()
    return scheduler
