from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, usuarios

app = FastAPI(
    title="SpecialPoints API",
    description="Sistema de pontos e recompensas para famílias",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)


@app.get("/", tags=["Health"])
async def health():
    return {"status": "ok", "servico": "SpecialPoints API"}
