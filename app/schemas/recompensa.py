from datetime import datetime

from pydantic import BaseModel, Field


class CriarRecompensaInput(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    descricao: str | None = None
    custo_pontos: int = Field(gt=0)
    estoque: int | None = Field(default=None, ge=0)
    imagem_url: str | None = None


class AtualizarRecompensaInput(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=200)
    descricao: str | None = None
    custo_pontos: int | None = Field(default=None, gt=0)
    estoque: int | None = Field(default=None, ge=0)
    imagem_url: str | None = None
    ativa: bool | None = None


class RecompensaPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    familia_id: int
    titulo: str
    descricao: str | None
    custo_pontos: int
    estoque: int | None
    ativa: bool
    imagem_url: str | None
    criado_em: datetime
    atualizado_em: datetime
