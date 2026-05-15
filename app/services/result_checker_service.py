import logging
from datetime import datetime
import httpx
from app.database import get_settings, SessionLocal
from app.models.pick_history import PickHistory

settings = get_settings()
BSD_BASE = "https://sports.bzzoiro.com/api"
logger = logging.getLogger(__name__)

# Mapeamento de mercado → função que avalia o placar
_CHECKERS = {
    "Over 2.5 gols":       lambda h, a: h + a > 2,
    "Over 1.5 gols":       lambda h, a: h + a > 1,
    "Over 3.5 gols":       lambda h, a: h + a > 3,
    "Under 2.5 gols":      lambda h, a: h + a < 3,
    "Ambas marcam (BTTS)": lambda h, a: h > 0 and a > 0,
    "Empate":              lambda h, a: h == a,
    "Vitória casa":        lambda h, a: h > a,
    "Vitória fora":        lambda h, a: a > h,
}


async def get_event_result(event_id: int) -> dict | None:
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{BSD_BASE}/events/{event_id}/",
                headers=headers,
            )
            if response.status_code != 200:
                return None
            return response.json()
    except (httpx.TimeoutException, httpx.HTTPError):
        return None


def check_pick_result(pick: PickHistory, event: dict) -> str | None:
    if event.get("status") != "finished":
        return None

    try:
        home_score = int(event.get("home_score") or 0)
        away_score = int(event.get("away_score") or 0)
    except (ValueError, TypeError):
        return None

    checker = _CHECKERS.get(pick.market)
    if checker is None:
        logger.warning("Mercado desconhecido para verificação: %s", pick.market)
        return None

    return "win" if checker(home_score, away_score) else "loss"


async def update_pending_results() -> dict:
    db = SessionLocal()
    checked = 0
    updated = 0

    try:
        pending = (
            db.query(PickHistory)
            .filter(PickHistory.result.is_(None))
            .all()
        )

        for pick in pending:
            if not pick.bsd_event_id:
                continue

            checked += 1
            event = await get_event_result(pick.bsd_event_id)
            if event is None:
                continue

            result = check_pick_result(pick, event)
            if result is None:
                continue

            pick.result = result
            pick.result_updated_at = datetime.utcnow()
            updated += 1

        if updated > 0:
            db.commit()

        remaining = (
            db.query(PickHistory)
            .filter(PickHistory.result.is_(None))
            .count()
        )

        return {"checked": checked, "updated": updated, "pending": remaining}

    except Exception:
        db.rollback()
        logger.exception("Erro ao atualizar resultados pendentes")
        return {"checked": checked, "updated": updated, "pending": -1}
    finally:
        db.close()
