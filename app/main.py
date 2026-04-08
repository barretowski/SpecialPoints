from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, auth, categorias, conquistas, metas, notificacoes, recompensas, resgates, tarefas, transacoes, usuarios

app = FastAPI(
    title="SpecialPoints API",
    description="Sistema de pontos e recompensas para famílias",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(conquistas.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(tarefas.router)
app.include_router(recompensas.router)
app.include_router(metas.router)
app.include_router(resgates.router)
app.include_router(transacoes.router)
app.include_router(notificacoes.router)


@app.get("/", tags=["Health"])
async def health():
    return {"status": "ok", "servico": "SpecialPoints API", "versao": "2.0.0"}
