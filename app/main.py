from fastapi import FastAPI
from app.database import engine, Base, get_settings
from app.routers import matches, analysis

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="API para análise de jogos de futebol"
)

Base.metadata.create_all(bind=engine)

app.include_router(matches.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"{settings.app_name} está rodando!"}