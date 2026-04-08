from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategoriaTarefa(Base):
    __tablename__ = "categorias_tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    icone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cor_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tarefas: Mapped[list["Tarefa"]] = relationship("Tarefa", back_populates="categoria")
