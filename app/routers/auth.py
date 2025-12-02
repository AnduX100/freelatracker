import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Deque, Dict, Optional
import threading

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth_utils import ALGORITHM, create_access_token, get_password_hash, verify_password
from ..config import get_access_token_exp_minutes, get_secret_key
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger("freelatracker.auth")

LOGIN_WINDOW_SECONDS = 300
LOGIN_MAX_ATTEMPTS = 10
_login_attempts: Dict[str, Deque[float]] = defaultdict(deque)
_rate_limit_lock = threading.Lock()


def _is_rate_limited(identifier: str) -> bool:
    now = time.time()
    with _rate_limit_lock:
        attempts = _login_attempts[identifier]
        while attempts and attempts[0] <= now - LOGIN_WINDOW_SECONDS:
            attempts.popleft()
        return len(attempts) >= LOGIN_MAX_ATTEMPTS


def _record_failed_attempt(identifier: str) -> None:
    now = time.time()
    with _rate_limit_lock:
        attempts = _login_attempts[identifier]
        attempts.append(now)


def _reset_attempts(identifier: str) -> None:
    with _rate_limit_lock:
        _login_attempts.pop(identifier, None)


def _is_token_revoked(db: Session, jti: Optional[str]) -> bool:
    if not jti:
        return False
    now = datetime.now(timezone.utc)
    return (
        db.query(models.RevokedToken)
        .filter(models.RevokedToken.jti == jti, models.RevokedToken.expires_at > now)
        .first()
        is not None
    )


def _revoke_token(db: Session, jti: str, expires_at: datetime) -> None:
    if not jti:
        return
    existing = db.query(models.RevokedToken).filter(models.RevokedToken.jti == jti).first()
    if existing:
        return
    record = models.RevokedToken(jti=jti, expires_at=expires_at)
    db.add(record)
    db.commit()


@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    email = user_in.email.strip().lower()
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado.",
        )

    hashed_pw = get_password_hash(user_in.password)

    user = models.User(
        email=email,
        hashed_password=hashed_pw,
    )
    db.add(user)
    db.commit()
    logger.info("User registered: %s", user.email)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None,
):
    email = form_data.username.strip().lower()
    client_id = request.client.host if request and request.client else "unknown"
    if _is_rate_limited(client_id):
        logger.warning("Login rate limited for %s", client_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Intenta de nuevo en unos minutos.",
        )

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        _record_failed_attempt(client_id)
        logger.warning("Invalid credentials for %s from %s", email, client_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=get_access_token_exp_minutes())
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    _reset_attempts(client_id)
    logger.info("Login success for %s from %s", email, client_id)

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        jti = payload.get("jti")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if _is_token_revoked(db, jti):
        raise credentials_exception

    return user


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales.",
        )

    jti = payload.get("jti")
    exp_ts = payload.get("exp")
    if not jti or exp_ts is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token sin identificador o expiración.",
        )
    expires_at = datetime.fromtimestamp(int(exp_ts), tz=timezone.utc)
    _revoke_token(db, jti, expires_at)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
