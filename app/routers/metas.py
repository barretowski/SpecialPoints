from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.meta import Meta, StatusMeta
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.meta import AtualizarMetaInput, CriarMetaInput, MetaPublica

router = APIRouter(prefix="/metas", tags=["Metas"])


@router.post("/", response_model=MetaPublica, status_code=status.HTTP_201_CREATED)
async def criar_meta(
    dados: CriarMetaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    if not responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Responsável não pertence a nenhuma família")

    meta = Meta(familia_id=responsavel.familia_id, **dados.model_dump())
    db.add(meta)
    await db.commit()
    await db.refresh(meta)
    return meta


@router.get("/", response_model=list[MetaPublica])
async def listar_metas(
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    query = select(Meta).where(Meta.familia_id == usuario.familia_id)

    if usuario.papel == PapelUsuario.filho:
        query = query.where(Meta.usuario_id == usuario.id)

    resultado = await db.execute(query.order_by(Meta.criado_em.desc()))
    return resultado.scalars().all()


@router.get("/{meta_id}", response_model=MetaPublica)
async def obter_meta(
    meta_id: int,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Meta).where(Meta.id == meta_id))
    meta = resultado.scalar_one_or_none()
    if not meta or meta.familia_id != usuario.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada")

    if usuario.papel == PapelUsuario.filho and meta.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return meta


@router.patch("/{meta_id}", response_model=MetaPublica)
async def atualizar_meta(
    meta_id: int,
    dados: AtualizarMetaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Meta).where(Meta.id == meta_id))
    meta = resultado.scalar_one_or_none()
    if not meta or meta.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada")

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(meta, campo, valor)

    await db.commit()
    await db.refresh(meta)
    return meta


@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_meta(
    meta_id: int,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Meta).where(Meta.id == meta_id))
    meta = resultado.scalar_one_or_none()
    if not meta or meta.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada")

    meta.status = StatusMeta.cancelada
    await db.commit()
