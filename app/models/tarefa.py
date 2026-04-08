import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatusTarefa(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"
    rejeitada = "rejeitada"
    expirada = "expirada"


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id"), nullable=False, index=True)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias_tarefas.id"), nullable=True, index=True)
    criado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    atribuido_a_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[StatusTarefa] = mapped_column(Enum(StatusTarefa), default=StatusTarefa.pendente, nullable=False, index=True)
    data_limite: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    familia: Mapped["Familia"] = relationship("Familia", back_populates="tarefas")
    categoria: Mapped["CategoriaTarefa | None"] = relationship("CategoriaTarefa", back_populates="tarefas")
    criado_por: Mapped["Usuario"] = relationship(
        "Usuario", foreign_keys=[criado_por_id], back_populates="tarefas_criadas"
    )
    atribuido_a: Mapped["Usuario | None"] = relationship(
        "Usuario", foreign_keys=[atribuido_a_id], back_populates="tarefas_atribuidas"
    )
    transacoes: Mapped[list["TransacaoPonto"]] = relationship("TransacaoPonto", back_populates="tarefa")
