from app.services.bsd_service import get_todays_events, get_event_predictions

# Pick simples — mantém os critérios atuais
MIN_PROBABILITY_SINGLE = 85.0
TARGET_ODD_MIN = 1.85
TARGET_ODD_MAX = 2.20

# Acumulador — critérios mais flexíveis para encontrar 2 jogos
MIN_PROBABILITY_ACCA = 75.0
ACCA_ODD_MIN = 1.80
ACCA_ODD_MAX = 2.30
ACCA_TARGET_TOTAL = 4.00


def extract_best_market(event: dict, prediction: dict | None,
                        min_prob: float = MIN_PROBABILITY_SINGLE,
                        odd_min: float = TARGET_ODD_MIN,
                        odd_max: float = TARGET_ODD_MAX) -> dict | None:
    if not prediction:
        return None

    markets = [
        {"market": "Over 2.5 gols",       "odd_key": "odds_over_25", "prob_key": "prob_over_25"},
        {"market": "Over 1.5 gols",       "odd_key": "odds_over_15", "prob_key": "prob_over_15"},
        {"market": "Ambas marcam (BTTS)", "odd_key": "odds_btts_yes","prob_key": "prob_btts_yes"},
        {"market": "Vitória casa",         "odd_key": "odds_home",    "prob_key": "prob_home_win"},
        {"market": "Vitória fora",         "odd_key": "odds_away",    "prob_key": "prob_away_win"},
    ]

    candidates = []
    for m in markets:
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
        if prob >= min_prob:
            candidates.append({
                "market": m["market"],
                "odd": odd,
                "probability": round(prob, 1),
                "confidence_score": (prob / 100) * odd
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
    }


async def find_daily_pick() -> dict | None:
    """Pick simples — 1 jogo com 85%+ e odd ~2.00."""
    events = await get_todays_events()
    best_pick = None
    best_score = 0

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(event, prediction)

        if market and market["confidence_score"] > best_score:
            best_score = market["confidence_score"]
            best_pick = build_event_pick(event, market)

    return best_pick


async def find_daily_acca() -> dict | None:
    """
    Acumulador — 2 jogos independentes com 75%+ e odd ~2.00 cada.
    Odd total alvo: ~4.00. Probabilidade combinada real exibida na mensagem.
    """
    events = await get_todays_events()
    candidates = []

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(
            event, prediction,
            min_prob=MIN_PROBABILITY_ACCA,
            odd_min=ACCA_ODD_MIN,
            odd_max=ACCA_ODD_MAX
        )
        if market:
            candidates.append(build_event_pick(event, market))

    if len(candidates) < 2:
        return None

    # Ordena por probabilidade e pega os 2 melhores
    candidates.sort(key=lambda x: x["probability"], reverse=True)
    leg1, leg2 = candidates[0], candidates[1]

    # Odd total e probabilidade combinada reais
    total_odd = round(leg1["odd"] * leg2["odd"], 2)
    combined_prob = round((leg1["probability"] / 100) * (leg2["probability"] / 100) * 100, 1)

    return {
        "legs": [leg1, leg2],
        "total_odd": total_odd,
        "combined_probability": combined_prob,
    }