import asyncio
import logging
from fastapi import APIRouter
from app.services.daily_pick_service import (
    find_daily_pick,
    find_daily_acca,
    save_picks_to_db,
)
from app.services.telegram_service import (
    send_daily_pick_notification,
    send_daily_acca_notification,
)

router = APIRouter(prefix="/daily-pick", tags=["daily-pick"])
logger = logging.getLogger(__name__)

# Mantém referencia forte aos background tasks para evitar GC pelo Python
# (asyncio.create_task so guarda weak ref — task pode sumir antes de terminar)
_background_tasks: set = set()


def _spawn(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


@router.get("/today")
async def get_todays_pick():
    """Busca e retorna o pick do dia manualmente (sem mandar no Telegram)."""
    pick = await find_daily_pick()
    if not pick:
        return {"message": "Nenhuma entrada com 85%+ encontrada hoje."}
    return pick


# ── Background jobs ─────────────────────────────────────────────

async def _notify_pick_job():
    logger.info("BG /today/notify iniciado")
    try:
        pick = await find_daily_pick()
        await send_daily_pick_notification(pick)
        save_picks_to_db(None, pick, None)
        logger.info("BG /today/notify concluido (pick=%s)", bool(pick))
    except Exception:
        logger.exception("BG /today/notify falhou")


async def _notify_acca_job():
    logger.info("BG /today/notify-acca iniciado")
    try:
        acca = await find_daily_acca()
        await send_daily_acca_notification(acca)
        save_picks_to_db(None, None, acca)
        logger.info("BG /today/notify-acca concluido (acca=%s)", bool(acca))
    except Exception:
        logger.exception("BG /today/notify-acca falhou")


async def _notify_all_job():
    logger.info("BG /today/notify-all iniciado")
    try:
        from app.services.bsd_service import (
            get_todays_events,
            get_all_predictions_today,
        )
        from app.services.daily_pick_service import find_conservative_pick
        from app.services.telegram_service import send_conservative_pick_notification

        events, predictions = await asyncio.gather(
            get_todays_events(),
            get_all_predictions_today(),
        )
        logger.info(
            "BG /today/notify-all: %d events + %d predictions fetched",
            len(events), len(predictions),
        )

        conservative, pick, acca = await asyncio.gather(
            find_conservative_pick(events, predictions),
            find_daily_pick(events, predictions),
            find_daily_acca(events, predictions),
        )
        logger.info(
            "BG /today/notify-all: picks gerados cons=%s bold=%s acca=%s",
            bool(conservative), bool(pick), bool(acca),
        )

        await send_conservative_pick_notification(conservative)
        await send_daily_pick_notification(pick)
        await send_daily_acca_notification(acca)
        save_picks_to_db(conservative, pick, acca)
        logger.info("BG /today/notify-all concluido")
    except Exception:
        logger.exception("BG /today/notify-all falhou")


# ── Endpoints ───────────────────────────────────────────────────

@router.post("/today/notify", status_code=202)
async def notify_todays_pick():
    """Dispara em background a geracao do pick arrojado + envio Telegram + save DB."""
    _spawn(_notify_pick_job())
    return {
        "status": "started",
        "message": "Pick arrojado em background — confira o Telegram e /api/picks/history em ~1min",
    }


@router.post("/today/notify-acca", status_code=202)
async def notify_todays_acca():
    """Dispara em background a geracao do acumulador + envio Telegram + save DB."""
    _spawn(_notify_acca_job())
    return {
        "status": "started",
        "message": "Acumulador em background — confira o Telegram e /api/picks/history em ~1min",
    }


@router.post("/today/notify-all", status_code=202)
async def notify_all():
    """Dispara em background os 3 picks com fetch unico de events+predictions."""
    _spawn(_notify_all_job())
    return {
        "status": "started",
        "message": "3 picks em background — confira o Telegram e /api/picks/history em ~1min",
    }


@router.get("/debug")
async def debug_todays_events():
    """Mostra os jogos de hoje com todos os campos brutos da BSD."""
    from app.services.bsd_service import get_todays_events
    events = await get_todays_events()
    if not events:
        return {"total": 0, "message": "Nenhum jogo retornado pela BSD hoje."}
    return {
        "total_jogos": len(events),
        "todas_as_chaves": list(events[0].keys()),
        "odds_e_probs": {
            k: v for k, v in events[0].items()
            if any(x in k.lower() for x in ["odd", "prob", "predict", "over", "btts", "goal"])
        },
        "jogo": f"{events[0].get('home_team')} vs {events[0].get('away_team')}"
    }


@router.get("/debug-prediction")
async def debug_prediction():
    """Mostra predições dos primeiros 3 jogos."""
    from app.services.bsd_service import get_todays_events, get_event_predictions
    events = await get_todays_events()
    if not events:
        return {"message": "Sem jogos hoje"}

    results = []
    for event in events[:3]:
        pred = await get_event_predictions(event.get("id"))
        results.append({
            "jogo": f"{event.get('home_team')} vs {event.get('away_team')}",
            "odds_over_25": event.get("odds_over_25"),
            "odds_btts_yes": event.get("odds_btts_yes"),
            "predicao_completa": pred
        })
    return results
