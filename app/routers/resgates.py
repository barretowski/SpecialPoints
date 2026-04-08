from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.notificacao import TipoNotificacao
from app.models.recompensa import Recompensa
from app.models.resgate import Resgate, StatusResgate
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.resgate import AvaliarResgateInput, ResgatePublico, SolicitarResgateInput
from app.services.pontos import debitar, notificar

router = APIRouter(prefix="/resgates", tags=["Resgates"])


@router.post("/", response_model=ResgatePublico, status_code=status.HTTP_201_CREATED)
async def solicitar_resgate(
    dados: SolicitarResgateInput,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Recompensa).where(Recompensa.id == dados.recompensa_id))
    recompensa = resultado.scalar_one_or_none()

    if not recompensa or recompensa.familia_id != usuario.familia_id or not recompensa.ativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recompensa não encontrada ou inativa")

    if usuario.pontos_disponiveis < recompensa.custo_pontos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pontos insuficientes. Necessário: {recompensa.custo_pontos}, disponível: {usuario.pontos_disponiveis}",
        )

    if recompensa.estoque is not None and recompensa.estoque <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recompensa sem estoque")

    await debitar(db, usuario, recompensa.custo_pontos, f'Resgate: "{recompensa.titulo}"')

    if recompensa.estoque is not None:
        recompensa.estoque -= 1

    resgate = Resgate(
        usuario_id=usuario.id,
        recompensa_id=recompensa.id,
        pontos_gastos=recompensa.custo_pontos,
        status=StatusResgate.pendente,
    )
    db.add(resgate)
    await db.flush()

    # Notifica responsáveis da família
    from app.models.usuario import PapelUsuario as Papel
    from sqlalchemy import select as sel

    responsaveis = await db.execute(
        sel(Usuario).where(
            Usuario.familia_id == usuario.familia_id,
            Usuario.papel == Papel.responsavel,
            Usuario.ativo == True,
        )
    )
    for resp in responsaveis.scalars():
        await notificar(
            db,
            resp.id,
            TipoNotificacao.resgate_aprovado,
            "Solicitação de resgate",
            f'{usuario.nome} solicitou a recompensa "{recompensa.titulo}".',
            referencia_id=resgate.id,
            referencia_tipo="resgate",
        )

    await db.commit()
    await db.refresh(resgate)
    return resgate


@router.get("/")
async def listar_resgates(
    status_filtro: StatusResgate | None = None,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    query = select(Resgate).options(selectinload(Resgate.usuario), selectinload(Resgate.recompensa))

    if usuario.papel == PapelUsuario.filho:
        query = query.where(Resgate.usuario_id == usuario.id)
    else:
        ids_familia = (await db.execute(
            select(Usuario.id).where(Usuario.familia_id == usuario.familia_id, Usuario.ativo == True)
        )).scalars().all()
        query = query.where(Resgate.usuario_id.in_(ids_familia))

    if status_filtro:
        query = query.where(Resgate.status == status_filtro)

    resgates = (await db.execute(query.order_by(Resgate.criado_em.desc()))).scalars().all()

    return [
        {
            **ResgatePublico.model_validate(r).model_dump(),
            "nome_usuario": r.usuario.nome if r.usuario else None,
            "titulo_recompensa": r.recompensa.titulo if r.recompensa else None,
        }
        for r in resgates
    ]


@router.patch("/{resgate_id}", response_model=ResgatePublico)
async def avaliar_resgate(
    resgate_id: int,
    dados: AvaliarResgateInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    if dados.status not in (StatusResgate.aprovado, StatusResgate.recusado, StatusResgate.entregue):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status inválido para avaliação")

    resultado = await db.execute(select(Resgate).where(Resgate.id == resgate_id))
    resgate = resultado.scalar_one_or_none()
    if not resgate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resgate não encontrado")

    resultado_filho = await db.execute(select(Usuario).where(Usuario.id == resgate.usuario_id))
    filho = resultado_filho.scalar_one_or_none()
    if not filho or filho.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resgate não pertence à sua família")

    if resgate.status != StatusResgate.pendente and dados.status != StatusResgate.entregue:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resgate já foi avaliado")

    if dados.status == StatusResgate.recusado:
        # Devolve os pontos
        from app.models.transacao_ponto import TipoTransacao
        from app.services.pontos import creditar

        resultado_recompensa = await db.execute(select(Recompensa).where(Recompensa.id == resgate.recompensa_id))
        recompensa = resultado_recompensa.scalar_one()

        await creditar(
            db,
            filho,
            resgate.pontos_gastos,
            TipoTransacao.credito,
            f'Estorno: resgate de "{recompensa.titulo}" recusado',
            aprovado_por_id=responsavel.id,
        )
        if recompensa.estoque is not None:
            recompensa.estoque += 1

    resgate.status = dados.status
    resgate.observacao = dados.observacao

    await notificar(
        db,
        filho.id,
        TipoNotificacao.resgate_aprovado,
        f"Resgate {dados.status.value}",
        f"Seu resgate foi {dados.status.value}."
        + (f" Observação: {dados.observacao}" if dados.observacao else ""),
        referencia_id=resgate.id,
        referencia_tipo="resgate",
    )

    await db.commit()
    await db.refresh(resgate)
    return resgate
