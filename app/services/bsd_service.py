import logging
import httpx
from datetime import date
from app.database import get_settings

settings = get_settings()
BSD_BASE = "https://sports.bzzoiro.com/api"
logger = logging.getLogger(__name__)


async def get_todays_events() -> list[dict]:
    today = date.today().isoformat()
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}
    url = f"{BSD_BASE}/events/"
    params: dict = {"date": today}
    events: list[dict] = []
    total_available: int | None = None
    seen_ids: set = set()
    duplicates = 0

    async with httpx.AsyncClient(timeout=60) as client:
        while url and len(events) < 500:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if total_available is None:
                total_available = data.get("count")
            for ev in data.get("results", []):
                eid = ev.get("id")
                if eid is None:
                    continue
                if eid in seen_ids:
                    duplicates += 1
                    continue
                seen_ids.add(eid)
                events.append(ev)
            url = data.get("next")
            params = {}

    logger.info(
        "BSD /events/ %s: %d jogos únicos de %s disponíveis (%d duplicatas removidas)",
        today, len(events), total_available, duplicates,
    )
    return events[:500]


async def get_event_predictions(event_id: int) -> dict | None:
    """
    Busca a predição do CatBoost para um evento.

    A BSD descontinuou GET /predictions/{event_id}/ (404) e agora expõe
    GET /predictions/?event={event_id}, com resposta paginada em
    {count, next, previous, results: [...]}. A predição vem em results[0].

    Os campos prob_under_15/25/35 não existem mais na resposta e são
    derivados como 100 - prob_over_X (complementares).
    """
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{BSD_BASE}/predictions/",
                headers=headers,
                params={"event": event_id},
            )
            if response.status_code != 200:
                logger.warning(
                    "BSD /predictions/?event=%s retornou HTTP %d",
                    event_id, response.status_code,
                )
                return None

            data = response.json()
            results = data.get("results") or []
            if not results:
                return None

            prediction = results[0]

            # Deriva prob_under_X a partir de prob_over_X (eventos complementares)
            for over_key, under_key in (
                ("prob_over_15", "prob_under_15"),
                ("prob_over_25", "prob_under_25"),
                ("prob_over_35", "prob_under_35"),
            ):
                over = prediction.get(over_key)
                if over is not None and under_key not in prediction:
                    try:
                        prediction[under_key] = 100 - float(over)
                    except (TypeError, ValueError):
                        pass

            return prediction

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(
            "BSD /predictions/?event=%s falhou: %s",
            event_id, type(e).__name__,
        )
        return None