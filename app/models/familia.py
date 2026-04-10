from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Familia(Base):
    __tablename__ = "familias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_convite: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="familia")
    tarefas: Mapped[list["Tarefa"]] = relationship("Tarefa", back_populates="familia")
    recompensas: Mapped[list["Recompensa"]] = relationship("Recompensa", back_populates="familia")
    metas: Mapped[list["Meta"]] = relationship("Meta", back_populates="familia")
