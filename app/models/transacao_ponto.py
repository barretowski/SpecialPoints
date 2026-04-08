import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoTransacao(str, enum.Enum):
    credito = "credito"
    debito = "debito"
    bonus = "bonus"
    expiracao = "expiracao"


class TransacaoPonto(Base):
    __tablename__ = "transacoes_pontos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    tarefa_id: Mapped[int | None] = mapped_column(ForeignKey("tarefas.id"), nullable=True, index=True)
    aprovado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao), nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_apos: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    usuario: Mapped["Usuario"] = relationship(
        "Usuario", foreign_keys=[usuario_id], back_populates="transacoes"
    )
    tarefa: Mapped["Tarefa | None"] = relationship("Tarefa", back_populates="transacoes")
    aprovado_por: Mapped["Usuario | None"] = relationship(
        "Usuario", foreign_keys=[aprovado_por_id], back_populates="transacoes_aprovadas"
    )
