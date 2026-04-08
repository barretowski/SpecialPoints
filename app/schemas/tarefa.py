from datetime import datetime

from pydantic import BaseModel, Field

from app.models.tarefa import StatusTarefa


class CriarTarefaInput(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    descricao: str | None = None
    pontos: int = Field(gt=0)
    categoria_id: int | None = None
    atribuido_a_id: int | None = None
    data_limite: datetime | None = None
    recorrencia: str | None = None  # diaria | semanal | mensal


class AtualizarTarefaInput(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=200)
    descricao: str | None = None
    pontos: int | None = Field(default=None, gt=0)
    categoria_id: int | None = None
    atribuido_a_id: int | None = None
    data_limite: datetime | None = None
    ativa: bool | None = None
    recorrencia: str | None = None


class RejeitarTarefaInput(BaseModel):
    observacao: str | None = None


class TarefaPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    familia_id: int
    categoria_id: int | None
    criado_por_id: int
    atribuido_a_id: int | None
    titulo: str
    descricao: str | None
    pontos: int
    status: StatusTarefa
    ativa: bool
    recorrencia: str | None
    data_limite: datetime | None
    concluida_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
