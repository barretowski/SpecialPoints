from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel, requer_super_responsavel
from app.models.usuario import PapelUsuario, Usuario
from app.schemas.usuario import AtualizarMembroInput, AtualizarUsuarioInput, UsuarioPublico
from app.services.auth import hash_senha, verificar_senha


class TrocarSenhaInput(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=6)


class CriarMembroFamiliaInput(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str
    senha: str = Field(min_length=6)
    papel: PapelUsuario = PapelUsuario.responsavel

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


@router.patch("/me/senha", response_model=UsuarioPublico)
async def trocar_senha(
    dados: TrocarSenhaInput,
    usuario: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
    if dados.senha_atual == dados.nova_senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A nova senha deve ser diferente da atual")

    usuario.senha_hash = hash_senha(dados.nova_senha)
    usuario.deve_trocar_senha = False
    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.post("/familia/membros", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
async def criar_membro_familia(
    dados: CriarMembroFamiliaInput,
    atual: Usuario = Depends(requer_super_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    if dados.papel in (PapelUsuario.admin, PapelUsuario.super_responsavel):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível criar responsável ou filho",
        )

    if not atual.familia_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pertence a nenhuma família")

    if (await db.execute(select(Usuario).where(Usuario.email == dados.email))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    novo = Usuario(
        familia_id=atual.familia_id,
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        papel=dados.papel,
        deve_trocar_senha=True,
    )
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return novo


@router.patch("/{usuario_id}", response_model=UsuarioPublico)
async def editar_membro(
    usuario_id: int,
    dados: AtualizarMembroInput,
    responsavel: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    alvo = resultado.scalar_one_or_none()

    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if alvo.familia_id != responsavel.familia_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não pertence à sua família")

    if dados.email and dados.email != alvo.email:
        existente = (await db.execute(select(Usuario).where(Usuario.email == dados.email))).scalar_one_or_none()
        if existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
        alvo.email = dados.email

    if dados.nome is not None:
        alvo.nome = dados.nome

    if dados.nova_senha is not None:
        alvo.senha_hash = hash_senha(dados.nova_senha)
        alvo.deve_trocar_senha = False

    await db.commit()
    await db.refresh(alvo)
    return alvo


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
