from datetime import datetime

from pydantic import BaseModel

from app.models.resgate import StatusResgate


class SolicitarResgateInput(BaseModel):
    recompensa_id: int


class AvaliarResgateInput(BaseModel):
    status: StatusResgate
    observacao: str | None = None


class ResgatePublico(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    usuario_id: int
    recompensa_id: int
    pontos_gastos: int
    status: StatusResgate
    observacao: str | None
    criado_em: datetime
    atualizado_em: datetime
