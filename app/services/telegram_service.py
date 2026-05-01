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
            json={
                "chat_id": settings.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
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
            json={
                "chat_id": settings.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
    return r.status_code == 200