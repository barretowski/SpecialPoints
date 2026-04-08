from datetime import datetime

from pydantic import BaseModel

from app.models.notificacao import TipoNotificacao


class NotificacaoPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    usuario_id: int
    tipo: TipoNotificacao
    titulo: str
    mensagem: str
    referencia_id: int | None
    referencia_tipo: str | None
    lida: bool
    criado_em: datetime
