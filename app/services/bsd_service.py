import logging
import time
import httpx
from datetime import date
from app.database import get_settings

settings = get_settings()
BSD_BASE = "https://sports.bzzoiro.com/api"
logger = logging.getLogger(__name__)


async def get_todays_events() -> list[dict]:
    today = date.today().isoformat()
    headers = {"Authorization": f"Token {settings.bsd_api_key}"}
    # Embute o filtro date na URL inicial em vez de usar params kwarg —
    # httpx 0.28 com params={} apaga a query string da URL na 2a pagina,
    # quebrando a paginacao silenciosamente.
    url: str | None = f"{BSD_BASE}/events/?date={today}"
    events: list[dict] = []
    total_available: int | None = None
    seen_ids: set = set()
    duplicates = 0
    pages_ok = 0
    pages_fail = 0
    MAX_PAGES = 20

    while url and len(events) < 500 and (pages_ok + pages_fail) < MAX_PAGES:
        page_num = pages_ok + pages_fail + 1
        t0 = time.time()
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(90.0, connect=10.0)
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            pages_fail += 1
            logger.warning(
                "BSD /events/ pagina %d falhou em %.1fs (%s) — interrompendo com %d parciais",
                page_num, time.time() - t0, type(e).__name__, len(events),
            )
            break

        logger.info("BSD /events/ pagina %d OK em %.1fs", page_num, time.time() - t0)
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
    # Idem get_todays_events: nao usar params kwarg em paginacao httpx 0.28
    url: str | None = f"{BSD_BASE}/predictions/"
    predictions: dict[int, dict] = {}
    total_available: int | None = None

    pages_ok = 0
    pages_fail = 0
    MAX_PAGES = 20

    while url and len(predictions) < 1000 and (pages_ok + pages_fail) < MAX_PAGES:
        # Cliente fresco por pagina
        page_num = pages_ok + pages_fail + 1
        t0 = time.time()
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(90.0, connect=10.0)
            ) as client:
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    logger.warning(
                        "BSD /predictions/ pagina %d HTTP %d em %.1fs — interrompendo com %d parciais",
                        page_num, response.status_code, time.time() - t0, len(predictions),
                    )
                    pages_fail += 1
                    break
                data = response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            pages_fail += 1
            logger.warning(
                "BSD /predictions/ pagina %d falhou em %.1fs (%s) — interrompendo com %d parciais",
                page_num, time.time() - t0, type(e).__name__, len(predictions),
            )
            break

        logger.info("BSD /predictions/ pagina %d OK em %.1fs", page_num, time.time() - t0)
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