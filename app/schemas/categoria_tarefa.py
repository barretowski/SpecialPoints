from datetime import datetime

from pydantic import BaseModel, Field


class CriarCategoriaInput(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    icone: str | None = Field(default=None, max_length=50)
    cor_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class AtualizarCategoriaInput(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=80)
    icone: str | None = None
    cor_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoriaPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    icone: str | None
    cor_hex: str | None
    criado_em: datetime
