import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual
from app.models.familia import Familia
from app.models.usuario import Usuario
from app.schemas.auth import LoginInput, TokenOutput
from app.schemas.usuario import RegistroInput, UsuarioPublico
from app.services.auth import (
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    hash_senha,
    verificar_senha,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registro", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
async def registrar(dados: RegistroInput, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Usuario).where(Usuario.email == dados.email))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    familia: Familia | None = None

    if dados.familia_codigo:
        resultado = await db.execute(select(Familia).where(Familia.codigo_convite == dados.familia_codigo))
        familia = resultado.scalar_one_or_none()
        if not familia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código de convite inválido")
    elif dados.familia_nome:
        familia = Familia(
            nome=dados.familia_nome,
            codigo_convite=secrets.token_urlsafe(8)[:12],
        )
        db.add(familia)
        await db.flush()

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        papel=dados.papel,
        familia_id=familia.id if familia else None,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenOutput)
async def login(dados: LoginInput, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Usuario).where(Usuario.email == dados.email, Usuario.ativo == True))
    usuario = resultado.scalar_one_or_none()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenOutput(
        access_token=criar_access_token(usuario.id, usuario.papel.value),
        refresh_token=criar_refresh_token(usuario.id, usuario.papel.value),
    )


@router.post("/refresh", response_model=TokenOutput)
async def renovar_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decodificar_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    usuario_id = int(payload["sub"])
    resultado = await db.execute(select(Usuario).where(Usuario.id == usuario_id, Usuario.ativo == True))
    usuario = resultado.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return TokenOutput(
        access_token=criar_access_token(usuario.id, usuario.papel.value),
        refresh_token=criar_refresh_token(usuario.id, usuario.papel.value),
    )


@router.get("/me", response_model=UsuarioPublico)
async def perfil_atual(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario
