from app.services.bsd_service import get_todays_events, get_event_predictions

MIN_PROBABILITY = 85.0      # BSD retorna em percentual (0-100)
TARGET_ODD_MIN = 1.85
TARGET_ODD_MAX = 2.20


def extract_best_market(event: dict, prediction: dict | None) -> dict | None:
    """
    Só analisa jogos COM predição da BSD.
    Probabilidades já vêm em formato percentual (ex: 54.79 = 54.79%).
    """
    if not prediction:
        return None

    markets = [
        {
            "market": "Over 2.5 gols",
            "odd_key": "odds_over_25",
            "prob_key": "prob_over_25",
            "recommend_key": "over_25_recommend"
        },
        {
            "market": "Over 1.5 gols",
            "odd_key": "odds_over_15",
            "prob_key": "prob_over_15",
            "recommend_key": "over_15_recommend"
        },
        {
            "market": "Ambas marcam (BTTS)",
            "odd_key": "odds_btts_yes",
            "prob_key": "prob_btts_yes",
            "recommend_key": "btts_recommend"
        },
        {
            "market": "Vitória casa",
            "odd_key": "odds_home",
            "prob_key": "prob_home_win",
            "recommend_key": "winner_recommend"
        },
        {
            "market": "Vitória fora",
            "odd_key": "odds_away",
            "prob_key": "prob_away_win",
            "recommend_key": "winner_recommend"
        },
    ]

    candidates = []

    for m in markets:
        # Pega odd do evento principal (não da predição)
        raw_odd = event.get(m["odd_key"])
        if raw_odd is None:
            continue
        try:
            odd = float(raw_odd)
        except (ValueError, TypeError):
            continue

        if not (TARGET_ODD_MIN <= odd <= TARGET_ODD_MAX):
            continue

        # Pega probabilidade da predição BSD (já em %)
        prob = prediction.get(m["prob_key"])
        if prob is None:
            continue

        prob = float(prob)

        if prob >= MIN_PROBABILITY:
            candidates.append({
                "market": m["market"],
                "odd": odd,
                "probability": round(prob, 1),
                "confidence_score": (prob / 100) * odd,
                "bsd_recommends": prediction.get(m["recommend_key"], False)
            })

    if not candidates:
        return None

    return max(candidates, key=lambda x: x["confidence_score"])


async def find_daily_pick() -> dict | None:
    events = await get_todays_events()
    best_pick = None
    best_score = 0

    for event in events:
        prediction = await get_event_predictions(event.get("id"))
        market = extract_best_market(event, prediction)

        if market and market["confidence_score"] > best_score:
            best_score = market["confidence_score"]
            league = event.get("league")
            best_pick = {
                "event_id": event.get("id"),
                "home_team": event.get("home_team"),
                "away_team": event.get("away_team"),
                "league": league.get("name", "—") if isinstance(league, dict) else "—",
                "kickoff": event.get("event_date", "—"),
                "market": market["market"],
                "odd": market["odd"],
                "probability": market["probability"],
                "bsd_recommends": market["bsd_recommends"],
            }

    return best_pick