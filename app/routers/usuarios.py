from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.usuario import AtualizarUsuarioInput, UsuarioPublico

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/familia", response_model=list[UsuarioPublico])
async def listar_membros_familia(
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    if not usuario.familia_id:
        return []
    resultado = await db.execute(
        select(Usuario).where(Usuario.familia_id == usuario.familia_id, Usuario.ativo == True)
    )
    return resultado.scalars().all()


@router.get("/{usuario_id}", response_model=UsuarioPublico)
async def obter_usuario(
    usuario_id: int,
    atual: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    alvo = resultado.scalar_one_or_none()

    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if atual.papel == PapelUsuario.filho and alvo.id != atual.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return alvo


@router.patch("/me", response_model=UsuarioPublico)
async def atualizar_perfil(
    dados: AtualizarUsuarioInput,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    if dados.nome is not None:
        usuario.nome = dados.nome
    if dados.avatar_url is not None:
        usuario.avatar_url = dados.avatar_url

    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desativar_usuario(
    usuario_id: int,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    alvo = resultado.scalar_one_or_none()

    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if alvo.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não pertence à sua família")

    alvo.ativo = False
    await db.commit()
