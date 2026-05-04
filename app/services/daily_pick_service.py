from datetime import datetime
from app.services.bsd_service import get_todays_events, get_event_predictions

# ── Critérios de seleção ──────────────────────────────────────────
CONSERVATIVE_ODD_MIN = 1.40
CONSERVATIVE_ODD_MAX = 1.65
CONSERVATIVE_MIN_PROB = 75.0

BOLD_ODD_MIN = 1.85
BOLD_ODD_MAX = 2.20
BOLD_MIN_PROB = 65.0

ACCA_ODD_MIN = 1.80
ACCA_ODD_MAX = 2.30
ACCA_MIN_PROB = 65.0

# ── Mercados analisados ───────────────────────────────────────────
MARKETS = [
    {"market": "Over 2.5 gols",       "odd_key": "odds_over_25", "prob_key": "prob_over_25"},
    {"market": "Over 1.5 gols",       "odd_key": "odds_over_15", "prob_key": "prob_over_15"},
    {"market": "Ambas marcam (BTTS)", "odd_key": "odds_btts_yes","prob_key": "prob_btts_yes"},
    {"market": "Vitória casa",         "odd_key": "odds_home",    "prob_key": "prob_home_win"},
    {"market": "Vitória fora",         "odd_key": "odds_away",    "prob_key": "prob_away_win"},
    {"market": "Over 3.5 gols",       "odd_key": "odds_over_35", "prob_key": "prob_over_35"},
]

# ── Pesos por liga ────────────────────────────────────────────────
LEAGUE_WEIGHTS = {
    # Tier 1
    "Premier League": 1.20,
    "La Liga": 1.20,
    "Bundesliga": 1.15,
    "Serie A": 1.15,
    "Ligue 1": 1.10,
    # Tier 2
    "Brasileirão Série A": 1.10,
    "Brazilian Serie A": 1.10,
    "Eredivisie": 1.05,
    "Primeira Liga": 1.05,
    "Championship": 1.05,
    "Liga Portugal": 1.05,
    "Super Lig": 1.05,
    "Saudi Pro League": 1.00,
    "MLS": 1.00,
    # Default
    "default": 0.85
}


# ── Funções de peso ───────────────────────────────────────────────

def get_league_weight(event: dict) -> float:
    league = event.get("league", {})
    name = league.get("name", "") if isinstance(league, dict) else ""
    return LEAGUE_WEIGHTS.get(name, LEAGUE_WEIGHTS["default"])


def get_form_weight(prediction: dict) -> float:
    """Usa xG esperado como proxy de forma recente dos times."""
    home_xg = prediction.get("expected_home_goals") or 1.0
    away_xg = prediction.get("expected_away_goals") or 1.0
    total_xg = float(home_xg) + float(away_xg)

    if total_xg >= 2.8:
        return 1.15
    elif total_xg >= 2.3:
        return 1.08
    elif total_xg >= 2.0:
        return 1.03
    elif total_xg <= 1.2:
        return 0.85
    elif total_xg <= 1.5:
        return 0.92
    return 1.0


def get_home_advantage_weight(market: str, event: dict) -> float:
    """Aplica bônus/penalidade para mercado de vitória casa."""
    if market != "Vitória casa":
        return 1.0
    is_neutral = event.get("is_neutral_ground") or False
    is_derby = event.get("is_local_derby") or False
    if is_neutral:
        return 0.90
    if is_derby:
        return 1.10
    return 1.05


def get_time_penalty(kickoff: str) -> float:
    """Penaliza jogos muito tarde — menos liquidez e dados ao vivo."""
    try:
        hour = datetime.fromisoformat(kickoff).hour
        if hour >= 22:
            return 0.88
        if hour >= 20:
            return 0.94
        return 1.0
    except Exception:
        return 1.0


def calculate_score(prob: float, odd: float, market: str,
                    event: dict, prediction: dict) -> float:
    """Score final ponderado por liga, forma, vantagem e horário."""
    base = (prob / 100) * odd
    score = (
        base
        * get_league_weight(event)
        * get_form_weight(prediction)
        * get_home_advantage_weight(market, event)
        * get_time_penalty(event.get("event_date", ""))
    )
    return round(score, 4)


# ── Lógica de seleção ─────────────────────────────────────────────

def extract_best_market(event: dict, prediction: dict | None,
                        min_prob: float,
                        odd_min: float,
                        odd_max: float) -> dict | None:
    if not prediction:
        return None

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
        if prob < min_prob:
            continue

        score = calculate_score(prob, odd, m["market"], event, prediction)
        candidates.append({
            "market": m["market"],
            "odd": odd,
            "probability": round(prob, 1),
            "confidence_score": score
        })

    if not candidates:
        return None

    return max(candidates, key=lambda x: x["confidence_score"])


def build_event_pick(event: dict, market: dict) -> dict:
    league = event.get("league")
    return {
        "event_id": event.get("id"),
        "home_team": event.get("home_team"),
        "away_team": event.get("away_team"),
        "league": league.get("name", "—") if isinstance(league, dict) else "—",
        "kickoff": event.get("event_date", "—"),
        "market": market["market"],
        "odd": market["odd"],
        "probability": market["probability"],
        "score": market["confidence_score"],
    }


# ── Picks públicos ────────────────────────────────────────────────

async def find_conservative_pick() -> dict | None:
    """Pick conservador — odd 1.40–1.65, prob 75%+, score ponderado."""
    events = await get_todays_events()
    best_pick = None
    best_score = 0

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(
            event, prediction,
            min_prob=CONSERVATIVE_MIN_PROB,
            odd_min=CONSERVATIVE_ODD_MIN,
            odd_max=CONSERVATIVE_ODD_MAX
        )
        if market and market["confidence_score"] > best_score:
            best_score = market["confidence_score"]
            best_pick = build_event_pick(event, market)

    return best_pick


async def find_daily_pick() -> dict | None:
    """Pick arrojado — odd 1.85–2.20, prob 65%+, score ponderado."""
    events = await get_todays_events()
    best_pick = None
    best_score = 0

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(
            event, prediction,
            min_prob=BOLD_MIN_PROB,
            odd_min=BOLD_ODD_MIN,
            odd_max=BOLD_ODD_MAX
        )
        if market and market["confidence_score"] > best_score:
            best_score = market["confidence_score"]
            best_pick = build_event_pick(event, market)

    return best_pick


async def find_daily_acca() -> dict | None:
    """Acumulador — 2 melhores jogos com score ponderado, odd total ~4.00."""
    events = await get_todays_events()
    candidates = []

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(
            event, prediction,
            min_prob=ACCA_MIN_PROB,
            odd_min=ACCA_ODD_MIN,
            odd_max=ACCA_ODD_MAX
        )
        if market:
            candidates.append(build_event_pick(event, market))

    if len(candidates) < 2:
        return None

    # Ordena pelo score ponderado — não só pela probabilidade bruta
    candidates.sort(key=lambda x: x["score"], reverse=True)
    leg1, leg2 = candidates[0], candidates[1]

    total_odd = round(leg1["odd"] * leg2["odd"], 2)
    combined_prob = round(
        (leg1["probability"] / 100) * (leg2["probability"] / 100) * 100, 1
    )

    return {
        "legs": [leg1, leg2],
        "total_odd": total_odd,
        "combined_probability": combined_prob,
    }