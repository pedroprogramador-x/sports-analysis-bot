import httpx
from datetime import date
from app.database import get_settings

settings = get_settings()
BSD_BASE = "https://sports.bzzoiro.com/api"


async def get_todays_events() -> list[dict]:
    today = date.today().isoformat()
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{BSD_BASE}/events/",
            headers=headers,
            params={"date": today}
        )
        response.raise_for_status()
        data = response.json()

    return data.get("results", [])


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
                return None

            return response.json()

    except (httpx.TimeoutException, httpx.HTTPError):
        return None