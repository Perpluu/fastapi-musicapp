import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal, get_db
from app.models import Song, Artist, Playlist, Review
from app.seed import seed_database
from app.auth import router as auth_router

# Konfiguracja zapisywania logów do pliku app.log (Kryterium: Inne - zapisywanie logów do pliku)
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
    version="0.2.0",
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


# Podpięcie routera autoryzacji REST (Etap 2)
app.include_router(auth_router)


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Endpoint diagnostyczny sprawdzający stan bazy danych."""
    return {
        "status": "ok",
        "stage": "Etap 2 - Autoryzacja REST, JWT, bcrypt i Role gotowe",
        "counts": {
            "artists": db.query(Artist).count(),
            "songs": db.query(Song).count(),
            "playlists": db.query(Playlist).count(),
            "reviews": db.query(Review).count(),
        },
    }