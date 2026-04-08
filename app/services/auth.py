from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)


def _criar_token(dados: dict, expire_delta: timedelta) -> str:
    payload = dados.copy()
    payload["exp"] = datetime.now(timezone.utc) + expire_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def criar_access_token(usuario_id: int, papel: str) -> str:
    return _criar_token(
        {"sub": str(usuario_id), "papel": papel, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def criar_refresh_token(usuario_id: int, papel: str) -> str:
    return _criar_token(
        {"sub": str(usuario_id), "papel": papel, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return {}
