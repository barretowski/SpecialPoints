from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuario import PapelUsuario, Usuario
from app.services.auth import decodificar_token

bearer_scheme = HTTPBearer()


async def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    payload = decodificar_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario_id = int(payload["sub"])
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id, Usuario.ativo == True))
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return usuario


def requer_papel(*papeis: PapelUsuario):
    async def verificar(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.papel not in papeis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito a: {', '.join(p.value for p in papeis)}",
            )
        return usuario

    return verificar


def requer_admin():
    return requer_papel(PapelUsuario.admin)


def requer_responsavel():
    # admin também pode agir como responsável em qualquer família
    return requer_papel(PapelUsuario.admin, PapelUsuario.responsavel)


def requer_filho():
    return requer_papel(PapelUsuario.filho)
