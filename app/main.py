import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal, get_db
from app.models import Song, Artist, Playlist, Review
from app.seed import seed_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("music_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicjalizacja bazy danych i danych początkowych przy starcie serwera."""
    logger.info("Uruchamianie serwera i inicjalizacja bazy danych SQL...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        logger.info("Baza danych gotowa (dane początkowe załadowane).")
    finally:
        db.close()
    yield
    logger.info("Zamykanie serwera aplikacji.")


app = FastAPI(
    title="PulseWave - Music Streaming & Multi-Protocol App",
    description="Projekt wykorzystujący HTTP REST, Cookies, WebSocket, SSE oraz MQTT",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    """Middleware logujący każde zapytanie HTTP do pliku app.log."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"HTTP {request.method} {request.url.path} - Status: {response.status_code} ({duration_ms:.2f}ms)"
    )
    return response


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Endpoint diagnostyczny sprawdzający stan bazy danych w Etapie 1."""
    return {
        "status": "ok",
        "stage": "Etap 1 - Baza danych i modele gotowe",
        "counts": {
            "artists": db.query(Artist).count(),
            "songs": db.query(Song).count(),
            "playlists": db.query(Playlist).count(),
            "reviews": db.query(Review).count(),
        },
    }