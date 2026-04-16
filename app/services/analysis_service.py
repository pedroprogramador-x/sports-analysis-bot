from app.schemas.match import MatchCreate
from app.schemas.analysis import AnalysisResponse


def _calculate_suggestion(diff: float) -> tuple[str, str]:
    if diff > 1.0:
        return "Over", "Alta"
    elif diff > 0.5:
        return "Over", "Média"
    elif diff < -1.0:
        return "Under", "Alta"
    elif diff < -0.5:
        return "Under", "Média"
    else:
        return "Evitar", "Baixa"


def analyze_match(match: MatchCreate, match_id: int) -> AnalysisResponse:
    goals_total = match.goals_avg_a + match.goals_avg_b
    corners_total = match.corners_avg_a + match.corners_avg_b

    goals_diff = goals_total - match.goals_line
    corners_diff = corners_total - match.corners_line

    goals_suggestion, goals_confidence = _calculate_suggestion(goals_diff)
    corners_suggestion, corners_confidence = _calculate_suggestion(corners_diff)

    return AnalysisResponse(
        id=0,
        match_id=match_id,
        goals_suggestion=goals_suggestion,
        goals_confidence=goals_confidence,
        goals_diff=round(goals_diff, 2),
        corners_suggestion=corners_suggestion,
        corners_confidence=corners_confidence,
        corners_diff=round(corners_diff, 2),
    )