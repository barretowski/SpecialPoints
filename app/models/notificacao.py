import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoNotificacao(str, enum.Enum):
    tarefa_atribuida = "tarefa_atribuida"
    tarefa_concluida = "tarefa_concluida"
    tarefa_aprovada = "tarefa_aprovada"
    tarefa_rejeitada = "tarefa_rejeitada"
    meta_atingida = "meta_atingida"
    resgate_aprovado = "resgate_aprovado"


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo: Mapped[TipoNotificacao] = mapped_column(Enum(TipoNotificacao), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    referencia_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    referencia_tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="notificacoes")
