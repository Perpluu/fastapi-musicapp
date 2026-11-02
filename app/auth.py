import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

logger = logging.getLogger("music_app")

# Konfiguracja JWT
SECRET_KEY = "super-secret-jwt-key-for-web-protocols-project-ug"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 godziny

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)

# Zbiór unieważnionych tokenów przy wylogowaniu (REST Logout)
revoked_tokens: set[str] = set()

router = APIRouter(prefix="/api/auth", tags=["Autoryzacja REST & JWT"])


# --- FUNKCJE POMOCNICZE (BCRYPT & JWT) ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def extract_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> Optional[str]:
    """Pobiera token JWT z nagłówka Authorization: Bearer lub z ciasteczka access_token."""
    if credentials and credentials.credentials:
        return credentials.credentials
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    return None


# --- ZALEŻNOŚCI SPRAWDZAJĄCE ROLE (ADMIN / USER / GUEST) ---
def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(extract_token),
) -> Optional[User]:
    """Zwraca obiekt User jeśli zalogowany, lub None jeśli użytkownik jest Gościem (Guest)."""
    if not token or token in revoked_tokens:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.username == username).first()


def require_user(current_user: Optional[User] = Depends(get_optional_user)) -> User:
    """Wymaga dowolnego zalogowanego użytkownika (rola: user, moderator lub admin)."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wymagane logowanie (rola Guest nie ma dostępu do tej akcji).",
        )
    return current_user


def require_admin(current_user: User = Depends(require_user)) -> User:
    """Wymaga roli 'admin' (np. do operacji CRUD na piosenkach i artystach)."""
    if current_user.role != "admin":
        logger.warning(
            f"Odmowa dostępu do panelu Admina dla użytkownika '{current_user.username}' (rola: {current_user.role})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień! Ta operacja wymaga roli Administratora (admin).",
        )
    return current_user


# --- ENDPOINTY REST AUTORYZACJI ---
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Rejestracja nowego użytkownika z hashowaniem hasła algorytmem bcrypt."""
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik o takiej nazwie już istnieje.",
        )

    new_user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Zarejestrowano nowego użytkownika: {new_user.username} (rola: {new_user.role})")
    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Logowanie REST: weryfikuje hasło bcrypt, wydaje token JWT i zapisuje go w ciasteczku."""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(f"Nieudana próba logowania dla loginu: {payload.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowa nazwa użytkownika lub hasło.",
        )

    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )

    logger.info(f"Użytkownik '{user.username}' (rola: {user.role}) zalogował się pomyślnie.")
    return TokenResponse(access_token=token, user=user)


@router.post("/logout")
def logout_user(
    response: Response,
    token: Optional[str] = Depends(extract_token),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Wylogowywanie REST: unieważnia token JWT i usuwa ciasteczko sesyjne."""
    if token:
        revoked_tokens.add(token)
    response.delete_cookie("access_token")

    username = current_user.username if current_user else "nieznany/guest"
    logger.info(f"Wylogowano użytkownika: {username}")
    return {"message": "Wylogowano pomyślnie.", "role": "guest"}


@router.get("/me")
def get_current_session(current_user: Optional[User] = Depends(get_optional_user)):
    """Zwraca informacje o aktualnie zalogowanym użytkowniku lub status Gościa (Guest)."""
    if not current_user:
        return {
            "authenticated": False,
            "user": {
                "id": None,
                "username": "Gość (Niezalogowany)",
                "role": "guest",
            },
        }
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
        },
    }