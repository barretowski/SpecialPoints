import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatusResgate(str, enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    recusado = "recusado"
    entregue = "entregue"


class Resgate(Base):
    __tablename__ = "resgates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    recompensa_id: Mapped[int] = mapped_column(ForeignKey("recompensas.id"), nullable=False, index=True)
    pontos_gastos: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[StatusResgate] = mapped_column(
        Enum(StatusResgate), default=StatusResgate.pendente, nullable=False, index=True
    )
    observacao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="resgates")
    recompensa: Mapped["Recompensa"] = relationship("Recompensa", back_populates="resgates")
