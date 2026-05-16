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
    pages_ok = 0
    pages_fail = 0

    async with httpx.AsyncClient(timeout=60) as client:
        while url and len(events) < 500:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                pages_fail += 1
                logger.warning(
                    "BSD /events/ pagina falhou (%s) — interrompendo com %d jogos parciais",
                    type(e).__name__, len(events),
                )
                break

            pages_ok += 1
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
        "BSD /events/ %s: %d jogos unicos (%d dups), %d/%d paginas, %s disponiveis",
        today, len(events), duplicates, pages_ok, pages_ok + pages_fail, total_available,
    )
    return events[:500]


def _augment_prediction(pred: dict) -> dict:
    """Adiciona prob_under_X derivado de prob_over_X (eventos complementares)."""
    for over_key, under_key in (
        ("prob_over_15", "prob_under_15"),
        ("prob_over_25", "prob_under_25"),
        ("prob_over_35", "prob_under_35"),
    ):
        over = pred.get(over_key)
        if over is not None and under_key not in pred:
            try:
                pred[under_key] = 100 - float(over)
            except (TypeError, ValueError):
                pass
    return pred


async def get_all_predictions_today() -> dict[int, dict]:
    """
    Busca TODAS as predições paginadas e indexa por event_id.

    A BSD ignora o filtro ?event= e sempre retorna todas as predições
    paginadas. Em vez de fazer N chamadas (todas pegando dados errados),
    fazemos a paginação completa uma vez e indexamos localmente.
    Retorna {event_id: prediction_dict}.
    """
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}
    url = f"{BSD_BASE}/predictions/"
    params: dict = {}
    predictions: dict[int, dict] = {}
    total_available: int | None = None

    pages_ok = 0
    pages_fail = 0

    async with httpx.AsyncClient(timeout=60) as client:
        while url and len(predictions) < 1000:
            try:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    logger.warning(
                        "BSD /predictions/ retornou HTTP %d — interrompendo com %d parciais",
                        response.status_code, len(predictions),
                    )
                    pages_fail += 1
                    break
                data = response.json()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                pages_fail += 1
                logger.warning(
                    "BSD /predictions/ pagina falhou (%s) — interrompendo com %d parciais",
                    type(e).__name__, len(predictions),
                )
                break

            pages_ok += 1
            if total_available is None:
                total_available = data.get("count")
            for pred in data.get("results", []):
                ev = pred.get("event")
                eid = ev.get("id") if isinstance(ev, dict) else ev
                if eid is None or eid in predictions:
                    continue
                predictions[eid] = _augment_prediction(pred)
            url = data.get("next")
            params = {}

    logger.info(
        "BSD /predictions/: %d predicoes indexadas, %d/%d paginas, %s disponiveis",
        len(predictions), pages_ok, pages_ok + pages_fail, total_available,
    )
    return predictions


async def get_event_predictions(event_id: int) -> dict | None:
    """
    Lookup de predição para um único evento. Faz fetch completo
    (paginado) e busca no dict. Útil para chamadas ad-hoc; para
    batches, use get_all_predictions_today() uma vez e passe o dict.
    """
    all_preds = await get_all_predictions_today()
    return all_preds.get(event_id)