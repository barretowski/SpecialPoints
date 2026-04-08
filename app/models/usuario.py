import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PapelUsuario(str, enum.Enum):
    admin = "admin"
    responsavel = "responsavel"
    filho = "filho"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    familia_id: Mapped[int | None] = mapped_column(ForeignKey("familias.id"), nullable=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[PapelUsuario] = mapped_column(Enum(PapelUsuario), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pontos_disponiveis: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pontos_acumulados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    familia: Mapped["Familia | None"] = relationship("Familia", back_populates="usuarios")
    transacoes: Mapped[list["TransacaoPonto"]] = relationship(
        "TransacaoPonto", foreign_keys="TransacaoPonto.usuario_id", back_populates="usuario"
    )
    transacoes_aprovadas: Mapped[list["TransacaoPonto"]] = relationship(
        "TransacaoPonto", foreign_keys="TransacaoPonto.aprovado_por_id", back_populates="aprovado_por"
    )
    tarefas_atribuidas: Mapped[list["Tarefa"]] = relationship(
        "Tarefa", foreign_keys="Tarefa.atribuido_a_id", back_populates="atribuido_a"
    )
    tarefas_criadas: Mapped[list["Tarefa"]] = relationship(
        "Tarefa", foreign_keys="Tarefa.criado_por_id", back_populates="criado_por"
    )
    resgates: Mapped[list["Resgate"]] = relationship("Resgate", back_populates="usuario")
    metas: Mapped[list["Meta"]] = relationship("Meta", back_populates="usuario")
    notificacoes: Mapped[list["Notificacao"]] = relationship("Notificacao", back_populates="usuario")
