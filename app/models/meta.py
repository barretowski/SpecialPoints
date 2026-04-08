import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatusMeta(str, enum.Enum):
    ativa = "ativa"
    concluida = "concluida"
    cancelada = "cancelada"


class Meta(Base):
    __tablename__ = "metas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id"), nullable=False, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    pontos_alvo: Mapped[int] = mapped_column(Integer, nullable=False)
    pontos_atuais: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[StatusMeta] = mapped_column(Enum(StatusMeta), default=StatusMeta.ativa, nullable=False, index=True)
    bonus_conclusao: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_limite: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    familia: Mapped["Familia"] = relationship("Familia", back_populates="metas")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="metas")
