# SpecialPoints — Guia para Claude

## O que é este projeto

Sistema de pontos e recompensas para famílias. Pais (responsáveis) criam tarefas para os filhos, que ganham pontos ao completá-las e podem trocar por recompensas.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend API | FastAPI (Python 3.13) |
| ORM | SQLAlchemy 2 async |
| Banco | PostgreSQL 17 — porta **5432** |
| Migrações | Alembic (driver síncrono: psycopg3) |
| Auth | JWT via `python-jose` + bcrypt |
| Frontend | Vue 3 + Vite + Pinia + Vue Router |
| HTTP client | Axios |

## Ambiente local

```
DATABASE_URL=postgresql+asyncpg://postgres:pgadmin@localhost:5432/specialpoints
SECRET_KEY=3f8a2d1e9c7b4f6a0e5d2c8b1a3f7e4d9c2b5a8e1f4d7c0b3a6e9f2d5c8b1a4
```

Banco de testes: `specialpoints_test` (mesmo servidor, mesmas credenciais).

## Como rodar

```bash
# Backend
uvicorn app.main:app --reload        # http://localhost:8000
# Docs: http://localhost:8000/docs

# Frontend
cd frontend && npm install && npm run dev   # http://localhost:5173

# Migrações (só quando mudar modelos)
alembic revision --autogenerate -m "descricao"
alembic upgrade head

# Testes
pytest tests/ -v
```

> **Alembic no Windows**: usa `psycopg` (v3) como driver síncrono.
> O driver assíncrono `asyncpg` é usado apenas pela aplicação.
> O .env usa porta **5432** (não 5433).

## Estrutura de arquivos

```
SpecialPoints/
├── app/
│   ├── main.py              # FastAPI app + CORS + routers
│   ├── config.py            # Settings (pydantic-settings, lê .env)
│   ├── database.py          # Engine async, Base, get_db()
│   ├── dependencies.py      # get_usuario_atual, requer_papel(), requer_responsavel()
│   ├── models/              # 9 tabelas SQLAlchemy
│   │   ├── familia.py
│   │   ├── usuario.py       # enum PapelUsuario: responsavel | filho
│   │   ├── categoria_tarefa.py
│   │   ├── tarefa.py        # enum StatusTarefa
│   │   ├── transacao_ponto.py  # enum TipoTransacao
│   │   ├── recompensa.py
│   │   ├── meta.py          # enum StatusMeta
│   │   ├── resgate.py       # enum StatusResgate
│   │   └── notificacao.py   # enum TipoNotificacao (6 tipos)
│   ├── schemas/             # Pydantic v2
│   │   ├── auth.py          # LoginInput, TokenOutput
│   │   ├── usuario.py       # RegistroInput, UsuarioPublico
│   │   ├── tarefa.py
│   │   ├── recompensa.py
│   │   ├── meta.py
│   │   ├── resgate.py
│   │   ├── transacao.py
│   │   ├── notificacao.py
│   │   ├── categoria_tarefa.py
│   │   └── paginacao.py     # class Paginacao (pagina, tamanho query params)
│   ├── routers/             # Um arquivo por domínio
│   │   ├── auth.py          # /auth/registro, /login, /refresh, /me
│   │   ├── usuarios.py      # /usuarios/familia, /{id}, /me
│   │   ├── categorias.py    # /categorias/
│   │   ├── tarefas.py       # /tarefas/ + /concluir /aprovar /rejeitar
│   │   ├── recompensas.py   # /recompensas/
│   │   ├── metas.py         # /metas/
│   │   ├── resgates.py      # /resgates/ + avaliação
│   │   ├── transacoes.py    # /transacoes/ + /bonus
│   │   └── notificacoes.py  # /notificacoes/ + marcar lida
│   └── services/
│       ├── auth.py          # hash_senha, criar_access_token, decodificar_token
│       └── pontos.py        # creditar, debitar, verificar_metas, notificar
├── alembic/
│   ├── env.py               # usa psycopg3 (síncrono) p/ migrações
│   └── versions/            # migrações geradas
├── tests/
│   ├── conftest.py          # fixtures: client, db, responsavel_token
│   ├── test_auth.py
│   └── test_tarefas.py
└── frontend/
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── assets/main.css  # CSS global com variáveis de design
    │   ├── router/index.js  # guards por papel (responsavel/filho)
    │   ├── stores/
    │   │   ├── auth.js      # login, logout, carregarPerfil
    │   │   └── notificacoes.js
    │   ├── services/
    │   │   ├── api.js       # axios + interceptor JWT + auto-refresh
    │   │   └── index.js     # todos os serviços por domínio
    │   └── views/
    │       ├── LoginView.vue
    │       ├── RegistroView.vue
    │       ├── responsavel/  # Layout sidebar + Dashboard, Tarefas, Recompensas, Membros
    │       └── filho/        # Layout mobile-first + Dashboard, Tarefas, Recompensas
    └── package.json
```

## Domínio — regras importantes

### Papéis
- `admin`: acesso total ao sistema (todas as famílias). Registro protegido por `ADMIN_SECRET`. `requer_responsavel()` também aceita admin.
- `responsavel`: cria tarefas, aprova/rejeita conclusões, gerencia recompensas e metas, concede bônus, avalia resgates.
- `filho`: conclui tarefas atribuídas a ele, solicita resgates, vê suas notificações.

### ADMIN_SECRET
Valor em `.env`: `sp-admin-2212`. Necessário no campo `admin_secret` do payload de registro para criar usuário admin.

### Fluxo de pontos
1. Responsável cria tarefa com `pontos`.
2. Filho conclui → status vira `em_andamento`.
3. Responsável aprova → `services/pontos.creditar()` é chamado, saldo atualizado, `verificar_metas()` roda.
4. Responsável rejeita → status vira `rejeitada`, filho notificado.

### Fluxo de resgate
1. Filho solicita → pontos debitados imediatamente, resgate fica `pendente`.
2. Responsável aprova/recusa → se recusado, pontos são estornados.

### Notificações (6 tipos)
`tarefa_atribuida`, `tarefa_concluida`, `tarefa_aprovada`, `tarefa_rejeitada`, `meta_atingida`, `resgate_aprovado`

### Paginação
Endpoints de listagem aceitam `?pagina=1&tamanho=20`.

## Fases do projeto

| Fase | Status | Conteúdo |
|---|---|---|
| 1 | ✅ Concluída | Setup, modelos, JWT auth |
| 2 | ✅ Concluída | Tarefas, pontos, recompensas, metas, resgates, notificações |
| 3 | ✅ Concluída | Categorias, paginação, testes, frontend Vue 3 (scaffold + views principais) |
| 4 | 🔲 Pendente | Interface do filho (acessibilidade aprimorada), polish geral |

## Convenções de código

- Campos e variáveis em **português** (ex: `pontos_disponiveis`, `familia_id`).
- Schemas Pydantic com sufixo `Input` (entrada) e `Publico/Publica` (saída).
- Dependências de autorização: `requer_responsavel()` e `requer_filho()` em `dependencies.py`.
- Modelos SQLAlchemy usam `Mapped` / `mapped_column` (estilo 2.0).
- Frontend usa Composition API com `<script setup>`.
