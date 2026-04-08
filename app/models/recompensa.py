from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Recompensa(Base):
    __tablename__ = "recompensas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id"), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    custo_pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    estoque: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    imagem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    familia: Mapped["Familia"] = relationship("Familia", back_populates="recompensas")
    resgates: Mapped[list["Resgate"]] = relationship("Resgate", back_populates="recompensa")
