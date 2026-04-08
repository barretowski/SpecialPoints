from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.transacao_ponto import TipoTransacao, TransacaoPonto
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.transacao import BonusManualInput, TransacaoPublica
from app.services.pontos import creditar

router = APIRouter(prefix="/transacoes", tags=["Transações de Pontos"])


@router.get("/", response_model=list[TransacaoPublica])
async def listar_transacoes(
    usuario_id: int | None = None,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.papel == PapelUsuario.filho:
        alvo_id = usuario.id
    else:
        alvo_id = usuario_id or usuario.id

    resultado = await db.execute(
        select(TransacaoPonto)
        .where(TransacaoPonto.usuario_id == alvo_id)
        .order_by(TransacaoPonto.criado_em.desc())
    )
    return resultado.scalars().all()


@router.post("/bonus", response_model=TransacaoPublica, status_code=status.HTTP_201_CREATED)
async def conceder_bonus(
    dados: BonusManualInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Usuario).where(Usuario.id == dados.usuario_id, Usuario.ativo == True)
    )
    filho = resultado.scalar_one_or_none()

    if not filho or filho.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado na sua família")

    transacao = await creditar(
        db,
        filho,
        dados.quantidade,
        TipoTransacao.bonus,
        dados.descricao,
        aprovado_por_id=responsavel.id,
    )

    from app.models.notificacao import TipoNotificacao
    from app.services.pontos import notificar

    await notificar(
        db,
        filho.id,
        TipoNotificacao.tarefa_aprovada,
        "Bônus recebido!",
        f'Você recebeu {dados.quantidade} pontos de bônus. "{dados.descricao}"',
    )

    await db.commit()
    await db.refresh(transacao)
    return transacao
