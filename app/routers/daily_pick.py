import asyncio
from fastapi import APIRouter
from app.services.daily_pick_service import find_daily_pick
from app.services.telegram_service import send_daily_pick_notification

router = APIRouter(prefix="/daily-pick", tags=["daily-pick"])


@router.get("/today")
def get_todays_pick():
    """Busca e retorna o pick do dia manualmente (sem mandar no Telegram)."""
    pick = asyncio.run(find_daily_pick())
    if not pick:
        return {"message": "Nenhuma entrada com 85%+ encontrada hoje."}
    return pick


@router.post("/today/notify")
def notify_todays_pick():
    """Busca o pick do dia e manda no Telegram manualmente."""
    pick = asyncio.run(find_daily_pick())
    asyncio.run(send_daily_pick_notification(pick))
    return {"sent": True, "pick": pick}


@router.get("/debug")
def debug_todays_events():
    import asyncio
    from app.services.bsd_service import get_todays_events
    events = asyncio.run(get_todays_events())
    if not events:
        return {"total": 0, "message": "Nenhum jogo retornado pela BSD hoje."}

    primeiro = events[0]
    return {
        "total_jogos": len(events),
        "todas_as_chaves": list(primeiro.keys()),
        "odds_e_probs": {
            k: v for k, v in primeiro.items()
            if any(x in k.lower() for x in ["odd", "prob", "predict", "over", "btts", "goal"])
        },
        "jogo": f"{primeiro.get('home_team')} vs {primeiro.get('away_team')}"
    }
@router.get("/debug-prediction")
def debug_prediction():
    import asyncio
    from app.services.bsd_service import get_todays_events, get_event_predictions
    events = asyncio.run(get_todays_events())
    if not events:
        return {"message": "Sem jogos hoje"}

    # Testa os 3 primeiros jogos
    results = []
    for event in events[:3]:
        pred = asyncio.run(get_event_predictions(event.get("id")))
        results.append({
            "jogo": f"{event.get('home_team')} vs {event.get('away_team')}",
            "odds_over_25": event.get("odds_over_25"),
            "odds_btts_yes": event.get("odds_btts_yes"),
            "predicao_completa": pred
        })
    return results