from datetime import datetime, timedelta
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.pick_history import PickHistory

router = APIRouter(prefix="/picks", tags=["pick-history"])


class ResultUpdate(BaseModel):
    result: Literal["win", "loss", "void"]


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=30)
    picks = (
        db.query(PickHistory)
        .filter(PickHistory.created_at >= cutoff)
        .order_by(PickHistory.created_at.desc())
        .all()
    )

    resolved = [p for p in picks if p.result in ("win", "loss")]
    wins = sum(1 for p in resolved if p.result == "win")
    losses = len(resolved) - wins
    win_rate = round(wins / len(resolved) * 100, 1) if resolved else None
    roi = (
        round(
            sum((p.odd - 1) if p.result == "win" else -1 for p in resolved)
            / len(resolved)
            * 100,
            1,
        )
        if resolved
        else None
    )

    return {
        "stats": {
            "total": len(picks),
            "resolved": len(resolved),
            "wins": wins,
            "losses": losses,
            "win_rate_pct": win_rate,
            "roi_pct": roi,
        },
        "picks": [
            {
                "id": p.id,
                "created_at": p.created_at,
                "home_team": p.home_team,
                "away_team": p.away_team,
                "league": p.league,
                "kickoff": p.kickoff,
                "market": p.market,
                "odd": p.odd,
                "probability": p.probability,
                "value": p.value,
                "pick_type": p.pick_type,
                "bsd_event_id": p.bsd_event_id,
                "result": p.result,
                "result_updated_at": p.result_updated_at,
            }
            for p in picks
        ],
    }


@router.get("/pending")
def get_pending(db: Session = Depends(get_db)):
    picks = (
        db.query(PickHistory)
        .filter(PickHistory.result.is_(None))
        .order_by(PickHistory.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "created_at": p.created_at,
            "home_team": p.home_team,
            "away_team": p.away_team,
            "league": p.league,
            "kickoff": p.kickoff,
            "market": p.market,
            "odd": p.odd,
            "pick_type": p.pick_type,
            "bsd_event_id": p.bsd_event_id,
        }
        for p in picks
    ]


async def _check_results_job():
    import logging
    logger = logging.getLogger(__name__)
    try:
        from app.services.result_checker_service import update_pending_results
        summary = await update_pending_results()
        logger.info("Background check-results: %s", summary)
    except Exception:
        logger.exception("Erro em background check-results")


@router.post("/check-results", status_code=202)
async def check_results():
    import asyncio
    asyncio.create_task(_check_results_job())
    return {
        "status": "started",
        "message": "Verificacao em background — resultado em /api/picks/history",
    }


@router.patch("/{pick_id}/result")
def update_result(pick_id: int, body: ResultUpdate, db: Session = Depends(get_db)):
    pick = db.query(PickHistory).filter(PickHistory.id == pick_id).first()
    if not pick:
        raise HTTPException(status_code=404, detail="Pick não encontrado")
    pick.result = body.result
    pick.result_updated_at = datetime.utcnow()
    db.commit()
    return {
        "id": pick.id,
        "result": pick.result,
        "result_updated_at": pick.result_updated_at,
    }
