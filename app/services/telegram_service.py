import httpx
from app.database import get_settings

settings = get_settings()
TELEGRAM_URL = f"https://api.telegram.org/bot{settings.telegram_token}"


async def send_analysis_notification(
    team_a: str, team_b: str,
    goals_suggestion: str, goals_confidence: str, goals_diff: float,
    corners_suggestion: str, corners_confidence: str, corners_diff: float
) -> bool:
    emoji_map = {"Over": "📈", "Under": "📉", "Evitar": "⚠️"}
    conf_map = {"Alta": "🟢", "Média": "🟡", "Baixa": "🔴"}
    message = (
        f"⚽ *{team_a} vs {team_b}*\n"
        f"{'─' * 28}\n"
        f"🥅 *GOLS*\n"
        f"  {emoji_map[goals_suggestion]} Sugestão: *{goals_suggestion}*\n"
        f"  {conf_map[goals_confidence]} Confiança: *{goals_confidence}*\n"
        f"  📊 Diferença: `{goals_diff:+.2f}`\n\n"
        f"🚩 *ESCANTEIOS*\n"
        f"  {emoji_map[corners_suggestion]} Sugestão: *{corners_suggestion}*\n"
        f"  {conf_map[corners_confidence]} Confiança: *{corners_confidence}*\n"
        f"  📊 Diferença: `{corners_diff:+.2f}`"
    )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
        )
    return r.status_code == 200


async def send_command_analysis(
    match_id: int, team_a: str, team_b: str,
    goals_suggestion: str, goals_confidence: str,
    corners_suggestion: str, corners_confidence: str
) -> bool:
    message = (
        f"🔍 *Consulta — Jogo #{match_id}*\n"
        f"⚽ {team_a} vs {team_b}\n"
        f"{'─' * 28}\n"
        f"🥅 Gols: *{goals_suggestion}* ({goals_confidence})\n"
        f"🚩 Escanteios: *{corners_suggestion}* ({corners_confidence})"
    )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
        )
    return r.status_code == 200


async def send_conservative_pick_notification(pick: dict | None) -> bool:
    if not pick:
        message = "🛡️ *Pick Conservador*\nNenhuma value bet encontrada hoje na faixa 1.30–1.75."
    else:
        value_pct = round(pick["value"] * 100, 1)
        message = (
            f"🛡️ *PICK CONSERVADOR*\n"
            f"{'─' * 28}\n"
            f"⚽ *{pick['home_team']} vs {pick['away_team']}*\n"
            f"🏆 {pick['league']}\n"
            f"🕐 {pick['kickoff']}\n\n"
            f"📌 Mercado: *{pick['market']}*\n"
            f"💰 Odd: *{pick['odd']}*\n"
            f"📊 Prob. estimada: *{pick['probability']}%*\n"
            f"{pick['value_emoji']} Value: *+{value_pct}%* ({pick['value_label']})"
        )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
        )
    return r.status_code == 200


async def send_daily_pick_notification(pick: dict | None) -> bool:
    if not pick:
        message = "🎯 *Pick Arrojado*\nNenhuma value bet encontrada hoje na faixa 1.75–3.00."
    else:
        value_pct = round(pick["value"] * 100, 1)
        message = (
            f"🎯 *PICK ARROJADO*\n"
            f"{'─' * 28}\n"
            f"⚽ *{pick['home_team']} vs {pick['away_team']}*\n"
            f"🏆 {pick['league']}\n"
            f"🕐 {pick['kickoff']}\n\n"
            f"📌 Mercado: *{pick['market']}*\n"
            f"💰 Odd: *{pick['odd']}*\n"
            f"📊 Prob. estimada: *{pick['probability']}%*\n"
            f"{pick['value_emoji']} Value: *+{value_pct}%* ({pick['value_label']})"
        )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
        )
    return r.status_code == 200


async def send_daily_acca_notification(acca: dict | None) -> bool:
    if not acca:
        message = "🎲 *Acumulador do dia*\nNão foram encontradas 2 value bets suficientes hoje."
    else:
        leg1, leg2 = acca["legs"]
        v1 = round(leg1["value"] * 100, 1)
        v2 = round(leg2["value"] * 100, 1)
        vc = round(acca["combined_value"] * 100, 1)
        message = (
            f"🎲 *ACUMULADOR DO DIA — Odd ~{acca['total_odd']}*\n"
            f"{'─' * 28}\n\n"
            f"1️⃣ *{leg1['home_team']} vs {leg1['away_team']}*\n"
            f"🏆 {leg1['league']}\n"
            f"📌 {leg1['market']} @ *{leg1['odd']}*\n"
            f"📊 Prob: {leg1['probability']}% | {leg1['value_emoji']} Value: +{v1}%\n\n"
            f"2️⃣ *{leg2['home_team']} vs {leg2['away_team']}*\n"
            f"🏆 {leg2['league']}\n"
            f"📌 {leg2['market']} @ *{leg2['odd']}*\n"
            f"📊 Prob: {leg2['probability']}% | {leg2['value_emoji']} Value: +{v2}%\n\n"
            f"{'─' * 28}\n"
            f"💰 Odd total: *{acca['total_odd']}*\n"
            f"📊 Prob. combinada: *{acca['combined_probability']}%*\n"
            f"🔢 Value total: *+{vc}%*"
        )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
        )
    return r.status_code == 200