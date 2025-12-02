from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from .config import get_access_token_exp_minutes, get_secret_key

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expiration = expires_delta or timedelta(minutes=get_access_token_exp_minutes())
    expire_at = datetime.now(timezone.utc) + expiration
    jti = to_encode.get("jti") or uuid4().hex
    to_encode.update({"jti": jti, "exp": expire_at})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt
