from fastapi import APIRouter
from app.services.daily_pick_service import find_daily_pick, find_daily_acca
from app.services.telegram_service import (
    send_daily_pick_notification,
    send_daily_acca_notification
)

router = APIRouter(prefix="/daily-pick", tags=["daily-pick"])


@router.get("/today")
async def get_todays_pick():
    """Busca e retorna o pick do dia manualmente (sem mandar no Telegram)."""
    pick = await find_daily_pick()
    if not pick:
        return {"message": "Nenhuma entrada com 85%+ encontrada hoje."}
    return pick


@router.post("/today/notify")
async def notify_todays_pick():
    """Busca o pick simples do dia e manda no Telegram."""
    pick = await find_daily_pick()
    await send_daily_pick_notification(pick)
    return {"sent": True, "pick": pick}


@router.post("/today/notify-acca")
async def notify_todays_acca():
    """Busca o acumulador do dia e manda no Telegram."""
    acca = await find_daily_acca()
    await send_daily_acca_notification(acca)
    return {"sent": True, "acca": acca}


@router.post("/today/notify-all")
async def notify_all():
    """Manda pick simples + acumulador no Telegram de uma vez."""
    pick = await find_daily_pick()
    acca = await find_daily_acca()
    await send_daily_pick_notification(pick)
    await send_daily_acca_notification(acca)
    return {"sent": True, "pick": pick, "acca": acca}


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