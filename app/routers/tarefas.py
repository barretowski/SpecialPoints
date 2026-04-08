from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.notificacao import TipoNotificacao
from app.schemas.paginacao import Paginacao
from app.models.tarefa import StatusTarefa, Tarefa
from app.models.transacao_ponto import TipoTransacao
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.tarefa import AtualizarTarefaInput, CriarTarefaInput, RejeitarTarefaInput, TarefaPublica
from app.services.pontos import creditar, notificar, verificar_metas

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def _assert_mesma_familia(tarefa: Tarefa, usuario: Usuario) -> None:
    if tarefa.familia_id != usuario.familia_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tarefa não pertence à sua família")


@router.post("/", response_model=TarefaPublica, status_code=status.HTTP_201_CREATED)
async def criar_tarefa(
    dados: CriarTarefaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    if not responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Responsável não pertence a nenhuma família")

    tarefa = Tarefa(
        familia_id=responsavel.familia_id,
        criado_por_id=responsavel.id,
        **dados.model_dump(),
    )
    db.add(tarefa)
    await db.flush()

    if dados.atribuido_a_id:
        await notificar(
            db,
            dados.atribuido_a_id,
            TipoNotificacao.tarefa_atribuida,
            "Nova tarefa atribuída",
            f'Você recebeu a tarefa "{tarefa.titulo}" ({tarefa.pontos} pts).',
            referencia_id=tarefa.id,
            referencia_tipo="tarefa",
        )

    await db.commit()
    await db.refresh(tarefa)
    return tarefa


@router.get("/", response_model=list[TarefaPublica])
async def listar_tarefas(
    status_filtro: StatusTarefa | None = None,
    usuario: Usuario = Depends(get_usuario_atual),
    paginacao: Paginacao = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(Tarefa).where(Tarefa.familia_id == usuario.familia_id)

    if usuario.papel == PapelUsuario.filho:
        query = query.where(Tarefa.atribuido_a_id == usuario.id, Tarefa.ativa == True)

    if status_filtro:
        query = query.where(Tarefa.status == status_filtro)

    resultado = await db.execute(query.order_by(Tarefa.criado_em.desc()).offset(paginacao.skip).limit(paginacao.limit))
    return resultado.scalars().all()


@router.get("/{tarefa_id}", response_model=TarefaPublica)
async def obter_tarefa(
    tarefa_id: int,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, usuario)
    return tarefa


@router.patch("/{tarefa_id}", response_model=TarefaPublica)
async def atualizar_tarefa(
    tarefa_id: int,
    dados: AtualizarTarefaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, responsavel)

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(tarefa, campo, valor)

    await db.commit()
    await db.refresh(tarefa)
    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_tarefa(
    tarefa_id: int,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, responsavel)
    await db.delete(tarefa)
    await db.commit()


@router.post("/{tarefa_id}/concluir", response_model=TarefaPublica)
async def concluir_tarefa(
    tarefa_id: int,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, usuario)

    if tarefa.status != StatusTarefa.pendente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tarefa não está pendente")

    if usuario.papel == PapelUsuario.filho and tarefa.atribuido_a_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tarefa não atribuída a você")

    tarefa.status = StatusTarefa.em_andamento
    tarefa.concluida_em = datetime.now(timezone.utc)

    await notificar(
        db,
        tarefa.criado_por_id,
        TipoNotificacao.tarefa_concluida,
        "Tarefa concluída",
        f'A tarefa "{tarefa.titulo}" foi marcada como concluída e aguarda aprovação.',
        referencia_id=tarefa.id,
        referencia_tipo="tarefa",
    )

    await db.commit()
    await db.refresh(tarefa)
    return tarefa


@router.post("/{tarefa_id}/aprovar", response_model=TarefaPublica)
async def aprovar_tarefa(
    tarefa_id: int,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, responsavel)

    if tarefa.status != StatusTarefa.em_andamento:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tarefa não está aguardando aprovação")

    if not tarefa.atribuido_a_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tarefa sem usuário atribuído")

    resultado_filho = await db.execute(select(Usuario).where(Usuario.id == tarefa.atribuido_a_id))
    filho = resultado_filho.scalar_one_or_none()
    if not filho:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário atribuído não encontrado")

    tarefa.status = StatusTarefa.concluida

    await creditar(
        db,
        filho,
        tarefa.pontos,
        TipoTransacao.credito,
        f'Tarefa concluída: "{tarefa.titulo}"',
        aprovado_por_id=responsavel.id,
        tarefa_id=tarefa.id,
    )
    await verificar_metas(db, filho, tarefa.pontos)
    await notificar(
        db,
        filho.id,
        TipoNotificacao.tarefa_aprovada,
        "Tarefa aprovada!",
        f'"{tarefa.titulo}" foi aprovada. Você ganhou {tarefa.pontos} pontos!',
        referencia_id=tarefa.id,
        referencia_tipo="tarefa",
    )

    await db.commit()
    await db.refresh(tarefa)
    return tarefa


@router.post("/{tarefa_id}/rejeitar", response_model=TarefaPublica)
async def rejeitar_tarefa(
    tarefa_id: int,
    dados: RejeitarTarefaInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    _assert_mesma_familia(tarefa, responsavel)

    if tarefa.status != StatusTarefa.em_andamento:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tarefa não está aguardando aprovação")

    tarefa.status = StatusTarefa.rejeitada
    tarefa.concluida_em = None

    if tarefa.atribuido_a_id:
        await notificar(
            db,
            tarefa.atribuido_a_id,
            TipoNotificacao.tarefa_rejeitada,
            "Tarefa rejeitada",
            f'"{tarefa.titulo}" foi rejeitada.'
            + (f" Motivo: {dados.observacao}" if dados.observacao else ""),
            referencia_id=tarefa.id,
            referencia_tipo="tarefa",
        )

    await db.commit()
    await db.refresh(tarefa)
    return tarefa
