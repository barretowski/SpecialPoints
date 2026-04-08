from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.usuario import PapelUsuario


class RegistroInput(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=6)
    papel: PapelUsuario
    familia_codigo: str | None = Field(default=None, description="Código de convite da família (para entrar numa existente)")
    familia_nome: str | None = Field(default=None, description="Nome da nova família (para responsável sem família)")


class UsuarioPublico(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    email: str
    papel: PapelUsuario
    avatar_url: str | None
    pontos_disponiveis: int
    pontos_acumulados: int
    familia_id: int | None
    ativo: bool
    criado_em: datetime


class AtualizarUsuarioInput(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    avatar_url: str | None = None
