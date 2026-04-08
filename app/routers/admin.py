from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import requer_admin
from app.models.familia import Familia
from app.models.notificacao import Notificacao
from app.models.recompensa import Recompensa
from app.models.resgate import Resgate
from app.models.tarefa import Tarefa
from app.models.transacao_ponto import TransacaoPonto
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.paginacao import Paginacao
from app.schemas.usuario import AtualizarUsuarioInput, UsuarioPublico

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Estatísticas gerais ────────────────────────────────────────────────────────

@router.get("/stats")
async def estatisticas(
    _: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    total_usuarios = (await db.execute(select(func.count()).select_from(Usuario))).scalar()
    total_familias = (await db.execute(select(func.count()).select_from(Familia))).scalar()
    total_tarefas = (await db.execute(select(func.count()).select_from(Tarefa))).scalar()
    total_transacoes = (await db.execute(select(func.count()).select_from(TransacaoPonto))).scalar()
    total_resgates = (await db.execute(select(func.count()).select_from(Resgate))).scalar()
    notif_nao_lidas = (
        await db.execute(select(func.count()).select_from(Notificacao).where(Notificacao.lida == False))
    ).scalar()

    return {
        "total_usuarios": total_usuarios,
        "total_familias": total_familias,
        "total_tarefas": total_tarefas,
        "total_transacoes": total_transacoes,
        "total_resgates": total_resgates,
        "notificacoes_nao_lidas": notif_nao_lidas,
    }


# ── Famílias ──────────────────────────────────────────────────────────────────

@router.get("/familias")
async def listar_familias(
    _: Usuario = Depends(requer_admin()),
    paginacao: Paginacao = Depends(),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Familia).order_by(Familia.criado_em.desc()).offset(paginacao.skip).limit(paginacao.limit)
    )
    familias = resultado.scalars().all()
    return [
        {
            "id": f.id,
            "nome": f.nome,
            "codigo_convite": f.codigo_convite,
            "criado_em": f.criado_em,
        }
        for f in familias
    ]


@router.delete("/familias/{familia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_familia(
    familia_id: int,
    _: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Familia).where(Familia.id == familia_id))
    familia = resultado.scalar_one_or_none()
    if not familia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Família não encontrada")
    await db.delete(familia)
    await db.commit()


# ── Usuários ──────────────────────────────────────────────────────────────────

@router.get("/usuarios", response_model=list[UsuarioPublico])
async def listar_usuarios(
    papel: PapelUsuario | None = None,
    ativo: bool | None = None,
    _: Usuario = Depends(requer_admin()),
    paginacao: Paginacao = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(Usuario)
    if papel:
        query = query.where(Usuario.papel == papel)
    if ativo is not None:
        query = query.where(Usuario.ativo == ativo)

    resultado = await db.execute(query.order_by(Usuario.criado_em.desc()).offset(paginacao.skip).limit(paginacao.limit))
    return resultado.scalars().all()


@router.get("/usuarios/{usuario_id}", response_model=UsuarioPublico)
async def obter_usuario(
    usuario_id: int,
    _: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioPublico)
async def atualizar_usuario(
    usuario_id: int,
    dados: AtualizarUsuarioInput,
    _: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(usuario, campo, valor)

    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.patch("/usuarios/{usuario_id}/papel", response_model=UsuarioPublico)
async def alterar_papel(
    usuario_id: int,
    novo_papel: PapelUsuario,
    admin: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    if usuario_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível alterar o próprio papel")

    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    usuario.papel = novo_papel
    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.patch("/usuarios/{usuario_id}/ativar", response_model=UsuarioPublico)
async def ativar_desativar_usuario(
    usuario_id: int,
    ativo: bool,
    admin: Usuario = Depends(requer_admin()),
    db: AsyncSession = Depends(get_db),
):
    if usuario_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível desativar a si mesmo")

    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    usuario.ativo = ativo
    await db.commit()
    await db.refresh(usuario)
    return usuario


# ── Transações (visão global) ─────────────────────────────────────────────────

@router.get("/transacoes")
async def listar_transacoes(
    usuario_id: int | None = None,
    _: Usuario = Depends(requer_admin()),
    paginacao: Paginacao = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(TransacaoPonto)
    if usuario_id:
        query = query.where(TransacaoPonto.usuario_id == usuario_id)

    resultado = await db.execute(
        query.order_by(TransacaoPonto.criado_em.desc()).offset(paginacao.skip).limit(paginacao.limit)
    )
    transacoes = resultado.scalars().all()
    return [
        {
            "id": t.id,
            "usuario_id": t.usuario_id,
            "tipo": t.tipo,
            "quantidade": t.quantidade,
            "saldo_apos": t.saldo_apos,
            "descricao": t.descricao,
            "criado_em": t.criado_em,
        }
        for t in transacoes
    ]
