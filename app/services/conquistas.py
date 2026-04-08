from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conquista import Conquista
from app.models.meta import Meta, StatusMeta
from app.models.resgate import Resgate
from app.models.tarefa import StatusTarefa, Tarefa
from app.models.usuario import Usuario

# Definição de todos os badges possíveis
DEFINICOES: list[dict] = [
    {
        "tipo": "primeira_tarefa",
        "titulo": "Primeira tarefa!",
        "descricao": "Concluiu a primeira tarefa",
        "icone": "🌟",
        "check": lambda s: s["tarefas"] >= 1,
    },
    {
        "tipo": "dez_tarefas",
        "titulo": "Dedicado",
        "descricao": "Concluiu 10 tarefas",
        "icone": "🔥",
        "check": lambda s: s["tarefas"] >= 10,
    },
    {
        "tipo": "cinquenta_tarefas",
        "titulo": "Campeão",
        "descricao": "Concluiu 50 tarefas",
        "icone": "🏆",
        "check": lambda s: s["tarefas"] >= 50,
    },
    {
        "tipo": "primeira_meta",
        "titulo": "Meta atingida!",
        "descricao": "Concluiu a primeira meta",
        "icone": "🎯",
        "check": lambda s: s["metas"] >= 1,
    },
    {
        "tipo": "primeiro_resgate",
        "titulo": "Primeiro prêmio!",
        "descricao": "Fez o primeiro resgate",
        "icone": "🎁",
        "check": lambda s: s["resgates"] >= 1,
    },
    {
        "tipo": "pontos_100",
        "titulo": "Centenário",
        "descricao": "Acumulou 100 pontos",
        "icone": "💯",
        "check": lambda s: s["pontos_acumulados"] >= 100,
    },
    {
        "tipo": "pontos_500",
        "titulo": "Explorador",
        "descricao": "Acumulou 500 pontos",
        "icone": "💎",
        "check": lambda s: s["pontos_acumulados"] >= 500,
    },
    {
        "tipo": "pontos_1000",
        "titulo": "Lendário",
        "descricao": "Acumulou 1000 pontos",
        "icone": "👑",
        "check": lambda s: s["pontos_acumulados"] >= 1000,
    },
]


async def verificar_e_conceder(db: AsyncSession, usuario: Usuario) -> list[Conquista]:
    """Verifica todas as condições de badges e concede os que ainda não foram ganhos."""
    existentes = set(
        (await db.execute(
            select(Conquista.tipo).where(Conquista.usuario_id == usuario.id)
        )).scalars().all()
    )

    tarefas_count = (await db.execute(
        select(func.count()).where(
            Tarefa.atribuido_a_id == usuario.id,
            Tarefa.status == StatusTarefa.concluida,
        )
    )).scalar() or 0

    metas_count = (await db.execute(
        select(func.count()).where(
            Meta.usuario_id == usuario.id,
            Meta.status == StatusMeta.concluida,
        )
    )).scalar() or 0

    resgates_count = (await db.execute(
        select(func.count()).where(Resgate.usuario_id == usuario.id)
    )).scalar() or 0

    stats = {
        "tarefas": tarefas_count,
        "metas": metas_count,
        "resgates": resgates_count,
        "pontos_acumulados": usuario.pontos_acumulados,
    }

    novas: list[Conquista] = []
    for defn in DEFINICOES:
        if defn["tipo"] not in existentes and defn["check"](stats):
            conquista = Conquista(
                usuario_id=usuario.id,
                tipo=defn["tipo"],
                titulo=defn["titulo"],
                descricao=defn["descricao"],
                icone=defn["icone"],
            )
            db.add(conquista)
            novas.append(conquista)

    return novas
