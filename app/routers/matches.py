from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.match import Match
from app.schemas.match import MatchCreate, MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchResponse, status_code=201)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    db_match = Match(
        team_a=match.team_a,
        team_b=match.team_b,
        goals_avg_a=match.goals_avg_a,
        goals_avg_b=match.goals_avg_b,
        corners_avg_a=match.corners_avg_a,
        corners_avg_b=match.corners_avg_b,
        goals_line=match.goals_line,
        corners_line=match.corners_line,
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@router.get("/", response_model=list[MatchResponse])
def list_matches(db: Session = Depends(get_db)):
    return db.query(Match).all()


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    return match