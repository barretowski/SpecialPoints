from datetime import datetime

from pydantic import BaseModel


class ConquistaPublica(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    usuario_id: int
    tipo: str
    titulo: str
    descricao: str
    icone: str
    conquistado_em: datetime
