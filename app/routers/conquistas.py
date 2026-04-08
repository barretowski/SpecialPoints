from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual
from app.models.conquista import Conquista
from app.models.usuario import Usuario
from app.schemas.conquista import ConquistaPublica

router = APIRouter(prefix="/conquistas", tags=["Conquistas"])


@router.get("/", response_model=list[ConquistaPublica])
async def listar_conquistas(
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Conquista)
        .where(Conquista.usuario_id == usuario.id)
        .order_by(Conquista.conquistado_em.asc())
    )
    return resultado.scalars().all()
