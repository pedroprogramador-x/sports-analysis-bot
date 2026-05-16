from datetime import datetime, timedelta
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.pick_history import PickHistory

router = APIRouter(prefix="/picks", tags=["pick-history"])

# Mantém referencia forte aos background tasks para evitar GC
_background_tasks: set = set()


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
    logger.info("BG /check-results iniciado")
    try:
        from app.services.result_checker_service import update_pending_results
        summary = await update_pending_results()
        logger.info("BG /check-results concluido: %s", summary)
    except Exception:
        logger.exception("BG /check-results falhou")


@router.post("/check-results", status_code=202)
async def check_results():
    import asyncio
    task = asyncio.create_task(_check_results_job())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return {
        "status": "started",
        "message": "Verificacao em background — resultado em /api/picks/history",
    }


@router.post("/diag/spawn-bg", status_code=202)
async def diag_spawn_bg():
    """Diagnostico: spawn background task que dorme 10s e escreve marker no banco.

    Se aparecer pick com pick_type='diagnostic' em /history apos ~15s,
    o fire-and-forget pattern funciona no Railway e o problema esta no
    fluxo BSD. Se nao aparecer, asyncio.create_task nao sobrevive ao
    fim da request handler no ambiente Railway.
    """
    import asyncio
    import logging
    from app.database import SessionLocal
    from app.models.pick_history import PickHistory

    log = logging.getLogger(__name__)

    async def _job():
        log.info("DIAG bg job iniciado")
        await asyncio.sleep(10)
        log.info("DIAG bg apos sleep 10s, escrevendo marker no banco")
        try:
            db = SessionLocal()
            db.add(PickHistory(
                home_team="DIAG",
                away_team="TEST",
                league="diagnostic",
                kickoff=datetime.utcnow().isoformat(),
                market="diag-marker",
                odd=1.0,
                probability=0.0,
                value=0.0,
                pick_type="diagnostic",
                bsd_event_id=None,
            ))
            db.commit()
            db.close()
            log.info("DIAG bg escreveu marker com sucesso")
        except Exception:
            log.exception("DIAG bg falhou no write")

    task = asyncio.create_task(_job())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return {"status": "spawned", "wait_seconds": 15, "check": "/api/picks/history"}


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
