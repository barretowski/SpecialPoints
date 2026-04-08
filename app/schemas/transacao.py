from datetime import datetime

from pydantic import BaseModel, Field

from app.models.transacao_ponto import TipoTransacao


class BonusManualInput(BaseModel):
    usuario_id: int
    quantidade: int = Field(gt=0)
    descricao: str = Field(min_length=1, max_length=300)


class TransacaoPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    usuario_id: int
    tarefa_id: int | None
    aprovado_por_id: int | None
    tipo: TipoTransacao
    quantidade: int
    saldo_apos: int
    descricao: str | None
    criado_em: datetime
