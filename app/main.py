from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base, get_settings
from app.routers import matches, analysis, auth
from app.routers import daily_pick
from app.services.scheduler_service import start_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(
    title=settings.app_name,
    version="4.0.0",
    description="API para análise de jogos com dados reais + pick diário automático",
    lifespan=lifespan
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(daily_pick.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"{settings.app_name} está rodando! 🚀"}