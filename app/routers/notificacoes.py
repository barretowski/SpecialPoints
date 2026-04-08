from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual
from app.models.notificacao import Notificacao
from app.models.usuario import Usuario
from app.schemas.notificacao import NotificacaoPublica

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("/", response_model=list[NotificacaoPublica])
async def listar_notificacoes(
    apenas_nao_lidas: bool = False,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notificacao).where(Notificacao.usuario_id == usuario.id)

    if apenas_nao_lidas:
        query = query.where(Notificacao.lida == False)

    resultado = await db.execute(query.order_by(Notificacao.criado_em.desc()))
    return resultado.scalars().all()


@router.patch("/{notificacao_id}/lida", response_model=NotificacaoPublica)
async def marcar_lida(
    notificacao_id: int,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Notificacao).where(Notificacao.id == notificacao_id))
    notificacao = resultado.scalar_one_or_none()

    if not notificacao or notificacao.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada")

    notificacao.lida = True
    await db.commit()
    await db.refresh(notificacao)
    return notificacao


@router.post("/marcar-todas-lidas", status_code=status.HTTP_204_NO_CONTENT)
async def marcar_todas_lidas(
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notificacao)
        .where(Notificacao.usuario_id == usuario.id, Notificacao.lida == False)
        .values(lida=True)
    )
    await db.commit()
