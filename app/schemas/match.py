from pydantic import BaseModel, Field


class MatchCreate(BaseModel):
    team_a: str = Field(min_length=2, max_length=100)
    team_b: str = Field(min_length=2, max_length=100)
    goals_avg_a: float = Field(gt=0, le=10)
    goals_avg_b: float = Field(gt=0, le=10)
    corners_avg_a: float = Field(gt=0, le=20)
    corners_avg_b: float = Field(gt=0, le=20)
    goals_line: float = Field(gt=0, le=10)
    corners_line: float = Field(gt=0, le=20)


class MatchResponse(BaseModel):
    id: int
    team_a: str
    team_b: str
    goals_avg_a: float
    goals_avg_b: float
    corners_avg_a: float
    corners_avg_b: float
    goals_line: float
    corners_line: float

    model_config = {"from_attributes": True}