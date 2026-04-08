from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.recompensa import Recompensa
from app.models.usuario import Usuario
from app.schemas.recompensa import AtualizarRecompensaInput, CriarRecompensaInput, RecompensaPublica

router = APIRouter(prefix="/recompensas", tags=["Recompensas"])


@router.post("/", response_model=RecompensaPublica, status_code=status.HTTP_201_CREATED)
async def criar_recompensa(
    dados: CriarRecompensaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    if not responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Responsável não pertence a nenhuma família")

    recompensa = Recompensa(familia_id=responsavel.familia_id, **dados.model_dump())
    db.add(recompensa)
    await db.commit()
    await db.refresh(recompensa)
    return recompensa


@router.get("/", response_model=list[RecompensaPublica])
async def listar_recompensas(
    incluir_inativas: bool = False,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    from app.models.usuario import PapelUsuario

    query = select(Recompensa).where(Recompensa.familia_id == usuario.familia_id)

    if usuario.papel == PapelUsuario.filho:
        # Filho: só vê ativas com estoque disponível
        query = query.where(
            Recompensa.ativa == True,
            (Recompensa.estoque == None) | (Recompensa.estoque > 0),
        )
    elif not incluir_inativas:
        # Responsável sem flag: só ativas
        query = query.where(Recompensa.ativa == True)
    # else: responsável com incluir_inativas=true → tudo

    resultado = await db.execute(query.order_by(Recompensa.ativa.desc(), Recompensa.custo_pontos))
    return resultado.scalars().all()


@router.get("/{recompensa_id}", response_model=RecompensaPublica)
async def obter_recompensa(
    recompensa_id: int,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Recompensa).where(Recompensa.id == recompensa_id))
    recompensa = resultado.scalar_one_or_none()
    if not recompensa or recompensa.familia_id != usuario.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recompensa não encontrada")
    return recompensa


@router.patch("/{recompensa_id}", response_model=RecompensaPublica)
async def atualizar_recompensa(
    recompensa_id: int,
    dados: AtualizarRecompensaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Recompensa).where(Recompensa.id == recompensa_id))
    recompensa = resultado.scalar_one_or_none()
    if not recompensa or recompensa.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recompensa não encontrada")

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(recompensa, campo, valor)

    await db.commit()
    await db.refresh(recompensa)
    return recompensa


@router.delete("/{recompensa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_recompensa(
    recompensa_id: int,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Recompensa).where(Recompensa.id == recompensa_id))
    recompensa = resultado.scalar_one_or_none()
    if not recompensa or recompensa.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recompensa não encontrada")
    recompensa.ativa = False
    await db.commit()
