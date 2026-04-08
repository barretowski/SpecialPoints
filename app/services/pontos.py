from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meta import Meta, StatusMeta
from app.models.notificacao import Notificacao, TipoNotificacao
from app.models.transacao_ponto import TipoTransacao, TransacaoPonto
from app.models.usuario import PapelUsuario, Usuario


async def creditar(
    db: AsyncSession,
    usuario: Usuario,
    quantidade: int,
    tipo: TipoTransacao,
    descricao: str,
    aprovado_por_id: int | None = None,
    tarefa_id: int | None = None,
    observacao: str | None = None,
) -> TransacaoPonto:
    if usuario.papel != PapelUsuario.filho:
        raise ValueError(f"Pontos só podem ser creditados a filhos. Papel recebido: {usuario.papel}")
    usuario.pontos_disponiveis += quantidade
    usuario.pontos_acumulados += quantidade

    transacao = TransacaoPonto(
        usuario_id=usuario.id,
        tarefa_id=tarefa_id,
        aprovado_por_id=aprovado_por_id,
        tipo=tipo,
        quantidade=quantidade,
        saldo_apos=usuario.pontos_disponiveis,
        descricao=descricao,
        observacao=observacao,
    )
    db.add(transacao)
    return transacao


async def debitar(
    db: AsyncSession,
    usuario: Usuario,
    quantidade: int,
    descricao: str,
    observacao: str | None = None,
) -> TransacaoPonto:
    if usuario.papel != PapelUsuario.filho:
        raise ValueError(f"Pontos só podem ser debitados de filhos. Papel recebido: {usuario.papel}")
    usuario.pontos_disponiveis -= quantidade

    transacao = TransacaoPonto(
        usuario_id=usuario.id,
        tipo=TipoTransacao.debito,
        quantidade=quantidade,
        saldo_apos=usuario.pontos_disponiveis,
        descricao=descricao,
        observacao=observacao,
    )
    db.add(transacao)
    return transacao


async def verificar_metas(
    db: AsyncSession,
    usuario: Usuario,
    pontos_ganhos: int,
) -> None:
    from sqlalchemy import select

    resultado = await db.execute(
        select(Meta).where(
            Meta.usuario_id == usuario.id,
            Meta.status == StatusMeta.ativa,
        )
    )
    metas = resultado.scalars().all()

    for meta in metas:
        if meta.status != StatusMeta.ativa:
            continue

        meta.pontos_atuais = min(meta.pontos_atuais + pontos_ganhos, meta.pontos_alvo)

        if meta.pontos_atuais >= meta.pontos_alvo:
            from datetime import datetime, timezone

            meta.status = StatusMeta.concluida
            meta.concluida_em = datetime.now(timezone.utc)

            if meta.bonus_conclusao > 0:
                await creditar(
                    db,
                    usuario,
                    meta.bonus_conclusao,
                    TipoTransacao.bonus,
                    f"Bônus pela conclusão da meta: {meta.titulo}",
                )

            notificacao = Notificacao(
                usuario_id=usuario.id,
                tipo=TipoNotificacao.meta_atingida,
                titulo="Meta concluída!",
                mensagem=f'Parabéns! Você concluiu a meta "{meta.titulo}".',
                referencia_id=meta.id,
                referencia_tipo="meta",
            )
            db.add(notificacao)


async def notificar(
    db: AsyncSession,
    usuario_id: int,
    tipo: TipoNotificacao,
    titulo: str,
    mensagem: str,
    referencia_id: int | None = None,
    referencia_tipo: str | None = None,
) -> Notificacao:
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        referencia_id=referencia_id,
        referencia_tipo=referencia_tipo,
    )
    db.add(notificacao)
    return notificacao
