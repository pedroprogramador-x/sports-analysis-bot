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

    async with httpx.AsyncClient(timeout=15) as client:
        while url and len(events) < 500:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if total_available is None:
                total_available = data.get("count")
            events.extend(data.get("results", []))
            url = data.get("next")
            params = {}

    logger.info(
        "BSD /events/ %s: %d jogos buscados de %s disponíveis",
        today, len(events), total_available,
    )
    return events[:500]


async def get_event_predictions(event_id: int) -> dict | None:
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{BSD_BASE}/predictions/{event_id}/",
                headers=headers
            )
            # 404 = sem predição, 502/503 = instabilidade BSD
            # Em qualquer erro retorna None sem quebrar o fluxo
            if response.status_code != 200:
                logger.warning(
                    "BSD /predictions/%s retornou HTTP %d",
                    event_id, response.status_code,
                )
                return None

            return response.json()

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(
            "BSD /predictions/%s falhou: %s",
            event_id, type(e).__name__,
        )
        return None