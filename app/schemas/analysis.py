from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    id: int
    match_id: int
    goals_suggestion: str
    goals_confidence: str
    goals_diff: float
    corners_suggestion: str
    corners_confidence: str
    corners_diff: float

    model_config = {"from_attributes": True}