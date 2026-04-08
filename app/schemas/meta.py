from datetime import datetime

from pydantic import BaseModel, Field

from app.models.meta import StatusMeta


class CriarMetaInput(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    descricao: str | None = None
    pontos_alvo: int = Field(gt=0)
    bonus_conclusao: int = Field(default=0, ge=0)
    usuario_id: int
    data_limite: datetime | None = None


class AtualizarMetaInput(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=200)
    descricao: str | None = None
    pontos_alvo: int | None = Field(default=None, gt=0)
    bonus_conclusao: int | None = Field(default=None, ge=0)
    data_limite: datetime | None = None


class MetaPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    familia_id: int
    usuario_id: int
    titulo: str
    descricao: str | None
    pontos_alvo: int
    pontos_atuais: int
    status: StatusMeta
    bonus_conclusao: int
    data_limite: datetime | None
    concluida_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
