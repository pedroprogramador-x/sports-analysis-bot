from fastapi import FastAPI
from app.database import engine, Base, get_settings
from app.routers import matches, analysis, auth

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="3.0.0",
    description="API para análise de jogos de futebol com Telegram e JWT"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"{settings.app_name} está rodando! 🚀"}