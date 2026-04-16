from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.match import Match
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import analyze_match

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{match_id}", response_model=AnalysisResponse, status_code=201)
def create_analysis(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    from app.schemas.match import MatchCreate
    match_data = MatchCreate(
        team_a=match.team_a,
        team_b=match.team_b,
        goals_avg_a=match.goals_avg_a,
        goals_avg_b=match.goals_avg_b,
        corners_avg_a=match.corners_avg_a,
        corners_avg_b=match.corners_avg_b,
        goals_line=match.goals_line,
        corners_line=match.corners_line,
    )

    result = analyze_match(match_data, match_id)

    db_analysis = Analysis(
        match_id=match_id,
        goals_suggestion=result.goals_suggestion,
        goals_confidence=result.goals_confidence,
        goals_diff=result.goals_diff,
        corners_suggestion=result.corners_suggestion,
        corners_confidence=result.corners_confidence,
        corners_diff=result.corners_diff,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


@router.get("/{match_id}", response_model=list[AnalysisResponse])
def get_analysis(match_id: int, db: Session = Depends(get_db)):
    analyses = db.query(Analysis).filter(Analysis.match_id == match_id).all()
    if not analyses:
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada")
    return analyses