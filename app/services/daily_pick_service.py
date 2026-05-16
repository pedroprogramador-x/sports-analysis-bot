import asyncio
import logging
from datetime import datetime
from app.services.bsd_service import (
    get_todays_events,
    get_event_predictions,
    get_all_predictions_today,
)

logger = logging.getLogger(__name__)

# ── Value Bet — critérios ─────────────────────────────────────────
MIN_VALUE = 0.05        # 5% de valor mínimo (conservador)
STRONG_VALUE = 0.10     # 10% de valor (forte)
VERY_STRONG_VALUE = 0.15 # 15% de valor (muito forte)

# ── Mercados analisados ───────────────────────────────────────────
MARKETS = [
    {"market": "Over 2.5 gols",       "odd_key": "odds_over_25", "prob_key": "prob_over_25"},
    {"market": "Over 1.5 gols",       "odd_key": "odds_over_15", "prob_key": "prob_over_15"},
    {"market": "Under 2.5 gols",      "odd_key": "odds_under_25","prob_key": "prob_under_25"},
    {"market": "Ambas marcam (BTTS)", "odd_key": "odds_btts_yes","prob_key": "prob_btts_yes"},
    {"market": "Empate",              "odd_key": "odds_draw",    "prob_key": "prob_draw"},
    {"market": "Vitória casa",         "odd_key": "odds_home",    "prob_key": "prob_home_win"},
    {"market": "Vitória fora",         "odd_key": "odds_away",    "prob_key": "prob_away_win"},
    {"market": "Over 3.5 gols",       "odd_key": "odds_over_35", "prob_key": "prob_over_35"},
]

# ── Pesos por liga ────────────────────────────────────────────────
LEAGUE_WEIGHTS = {
    "Premier League": 1.20,
    "La Liga": 1.20,
    "Bundesliga": 1.15,
    "Serie A": 1.15,
    "Ligue 1": 1.10,
    "Brasileirão Série A": 1.10,
    "Brazilian Serie A": 1.10,
    "Champions League": 1.20,
    "Europa League": 1.10,
    "Eredivisie": 1.05,
    "Primeira Liga": 1.05,
    "Championship": 1.05,
    "Liga Portugal": 1.05,
    "Super Lig": 1.00,
    "Saudi Pro League": 0.95,
    "MLS": 0.95,
    "default": 0.85
}


# ── Funções auxiliares ────────────────────────────────────────────

def get_league_weight(event: dict) -> float:
    league = event.get("league", {})
    name = league.get("name", "") if isinstance(league, dict) else ""
    return LEAGUE_WEIGHTS.get(name, LEAGUE_WEIGHTS["default"])


def get_time_penalty(kickoff: str) -> float:
    try:
        hour = datetime.fromisoformat(kickoff).hour
        if hour >= 22:
            return 0.88
        if hour >= 20:
            return 0.94
        return 1.0
    except Exception:
        return 1.0


def get_injury_penalty(event: dict) -> float:
    unavailable = event.get("unavailable_players")
    if not unavailable or not isinstance(unavailable, dict):
        return 1.0
    count = 0
    for side in ("home", "away"):
        players = unavailable.get(side) or []
        count += sum(1 for p in players if p.get("status") in ("injured", "doubtful"))
    if count >= 3:
        return 0.90
    if count >= 1:
        return 0.95
    return 1.0


def calculate_value(prob: float, odd: float) -> float:
    """
    Fórmula de Value Bet:
    Value = (probabilidade_real × odd) - 1
    Positivo = mercado está pagando mais do que deveria.
    """
    return round((prob / 100) * odd - 1, 4)


def value_label(value: float) -> tuple[str, str]:
    """Retorna emoji e label baseado no valor encontrado."""
    if value >= VERY_STRONG_VALUE:
        return "🔥", "Muito Forte"
    elif value >= STRONG_VALUE:
        return "🟢", "Forte"
    elif value >= MIN_VALUE:
        return "🟡", "Moderado"
    else:
        return "🔴", "Sem valor"


def extract_best_value_bet(event: dict, prediction: dict | None,
                           min_value: float = MIN_VALUE,
                           odd_min: float = 1.30,
                           odd_max: float = 3.50) -> dict | None:
    """
    Encontra o mercado com maior Value positivo no jogo.
    Não exige probabilidade mínima — exige VALOR mínimo.
    """
    if not prediction:
        return None

    league_weight = get_league_weight(event)
    time_penalty = get_time_penalty(event.get("event_date", ""))
    injury_penalty = get_injury_penalty(event)
    candidates = []

    for m in MARKETS:
        raw_odd = event.get(m["odd_key"])
        if raw_odd is None:
            continue
        try:
            odd = float(raw_odd)
        except (ValueError, TypeError):
            continue

        if not (odd_min <= odd <= odd_max):
            continue

        prob = prediction.get(m["prob_key"])
        if prob is None:
            continue

        prob = float(prob)
        value = calculate_value(prob, odd)

        adjusted_value = value * time_penalty * injury_penalty
        effective_min = min_value / league_weight

        if adjusted_value >= effective_min:
            emoji, label = value_label(adjusted_value)
            candidates.append({
                "market": m["market"],
                "odd": odd,
                "probability": round(prob, 1),
                "value": round(adjusted_value, 4),
                "value_label": label,
                "value_emoji": emoji,
            })

    if not candidates:
        return None

    return max(candidates, key=lambda x: x["value"])


def build_event_pick(event: dict, market: dict) -> dict:
    league = event.get("league")
    ai_raw = event.get("ai_preview")
    if isinstance(ai_raw, dict):
        preview = (ai_raw.get("text") or "")[:150] or None
    elif isinstance(ai_raw, str):
        preview = ai_raw[:150] or None
    else:
        preview = None
    return {
        "event_id": event.get("id"),
        "home_team": event.get("home_team"),
        "away_team": event.get("away_team"),
        "league": league.get("name", "—") if isinstance(league, dict) else "—",
        "kickoff": event.get("event_date", "—"),
        "market": market["market"],
        "odd": market["odd"],
        "probability": market["probability"],
        "value": market["value"],
        "value_label": market["value_label"],
        "value_emoji": market["value_emoji"],
        "ai_preview": preview,
    }


# ── Picks públicos ────────────────────────────────────────────────

async def find_conservative_pick(
    events: list[dict] | None = None,
    predictions: dict[int, dict] | None = None,
) -> dict | None:
    """Value bet conservador — odd 1.30–1.75, valor mínimo 5%."""
    if events is None:
        events = await get_todays_events()
    if not events:
        return None
    if predictions is None:
        predictions = await get_all_predictions_today()

    best_pick = None
    best_value = 0

    for event in events:
        prediction = predictions.get(event.get("id"))
        if prediction is None:
            continue
        market = extract_best_value_bet(
            event, prediction,
            min_value=MIN_VALUE,
            odd_min=1.30,
            odd_max=1.75
        )
        if market and market["value"] > best_value:
            best_value = market["value"]
            best_pick = build_event_pick(event, market)

    return best_pick


async def find_daily_pick(
    events: list[dict] | None = None,
    predictions: dict[int, dict] | None = None,
) -> dict | None:
    """Value bet arrojado — odd 1.75–3.00, valor mínimo 8%."""
    if events is None:
        events = await get_todays_events()
    if not events:
        return None
    if predictions is None:
        predictions = await get_all_predictions_today()

    best_pick = None
    best_value = 0

    for event in events:
        prediction = predictions.get(event.get("id"))
        if prediction is None:
            continue
        market = extract_best_value_bet(
            event, prediction,
            min_value=0.08,
            odd_min=1.75,
            odd_max=3.00
        )
        if market and market["value"] > best_value:
            best_value = market["value"]
            best_pick = build_event_pick(event, market)

    return best_pick


async def find_daily_acca(
    events: list[dict] | None = None,
    predictions: dict[int, dict] | None = None,
) -> dict | None:
    """Acumulador — 2 value bets com valor 5%+, odd total ~3.00-6.00."""
    if events is None:
        events = await get_todays_events()
    if not events:
        return None
    if predictions is None:
        predictions = await get_all_predictions_today()

    candidates = []
    for event in events:
        prediction = predictions.get(event.get("id"))
        if prediction is None:
            continue
        market = extract_best_value_bet(
            event, prediction,
            min_value=MIN_VALUE,
            odd_min=1.50,
            odd_max=2.50
        )
        if market:
            candidates.append(build_event_pick(event, market))

    if len(candidates) < 2:
        return None

    candidates.sort(key=lambda x: x["value"], reverse=True)
    leg1 = candidates[0]
    # leg2 precisa ser de outro evento — bookmakers nao aceitam acca
    # com dois mercados do mesmo jogo, e a prob combinada precisa de
    # eventos independentes
    leg2 = next(
        (c for c in candidates[1:] if c["event_id"] != leg1["event_id"]),
        None,
    )
    if leg2 is None:
        return None

    total_odd = round(leg1["odd"] * leg2["odd"], 2)
    combined_prob = round(
        (leg1["probability"] / 100) * (leg2["probability"] / 100) * 100, 1
    )
    combined_value = round(leg1["value"] + leg2["value"], 4)

    return {
        "legs": [leg1, leg2],
        "total_odd": total_odd,
        "combined_probability": combined_prob,
        "combined_value": combined_value,
    }


def save_picks_to_db(
    conservative: dict | None,
    bold: dict | None,
    acca: dict | None,
) -> None:
    from app.database import SessionLocal
    from app.models.pick_history import PickHistory

    def _record(pick: dict, pick_type: str) -> PickHistory:
        return PickHistory(
            home_team=pick.get("home_team", ""),
            away_team=pick.get("away_team", ""),
            league=pick.get("league", ""),
            kickoff=str(pick.get("kickoff", "")),
            market=pick.get("market", ""),
            odd=float(pick.get("odd", 0)),
            probability=float(pick.get("probability", 0)),
            value=float(pick.get("value", 0)),
            pick_type=pick_type,
            bsd_event_id=pick.get("event_id"),
        )

    records = []
    if conservative:
        records.append(_record(conservative, "conservative"))
    if bold:
        records.append(_record(bold, "bold"))
    if acca:
        for leg in acca.get("legs", []):
            records.append(_record(leg, "acca_leg"))

    if not records:
        return

    db = SessionLocal()
    try:
        db.add_all(records)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Erro ao salvar picks no banco")
    finally:
        db.close()