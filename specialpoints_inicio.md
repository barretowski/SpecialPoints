# SpecialPoints — Documentação do Projeto

## Visão geral

Sistema web de pontos e recompensas para famílias. Pais (responsáveis) criam tarefas para seus filhos. Ao concluir e ter a tarefa aprovada, o filho ganha pontos que pode trocar por recompensas cadastradas pelos pais.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Python 3.13 |
| ORM | SQLAlchemy 2 (async) |
| Banco de dados | PostgreSQL 17 |
| Migrações | Alembic + psycopg3 (driver síncrono) |
| Autenticação | JWT (access + refresh token) |
| Frontend | Vue 3 + Vite + Pinia + Vue Router |
| HTTP client | Axios |

## Banco de dados — 9 tabelas

| Tabela | Descrição |
|---|---|
| `familias` | Grupos familiares com código de convite |
| `usuarios` | Responsáveis e filhos (papel: `responsavel` \| `filho`) |
| `categorias_tarefas` | Categorias reutilizáveis para tarefas |
| `tarefas` | Tarefas com pontos, status e atribuição |
| `transacoes_pontos` | Histórico de crédito/débito/bônus |
| `recompensas` | Itens resgatáveis com custo em pontos |
| `metas` | Metas de acumulação de pontos com bônus |
| `resgates` | Solicitações de resgate de recompensas |
| `notificacoes` | Notificações in-app (6 tipos) |

## Endpoints da API

### Autenticação (`/auth`)
| Método | Rota | Papel |
|---|---|---|
| POST | `/auth/registro` | público |
| POST | `/auth/login` | público |
| POST | `/auth/refresh` | público |
| GET | `/auth/me` | autenticado |

### Usuários (`/usuarios`)
| Método | Rota | Papel |
|---|---|---|
| GET | `/usuarios/familia` | autenticado |
| GET | `/usuarios/{id}` | autenticado |
| PATCH | `/usuarios/me` | autenticado |
| DELETE | `/usuarios/{id}` | responsavel |

### Categorias (`/categorias`)
CRUD completo — `POST`, `GET`, `PATCH /{id}`, `DELETE /{id}`
Criação/edição: responsavel. Leitura: autenticado.

### Tarefas (`/tarefas`)
| Método | Rota | Papel |
|---|---|---|
| POST | `/tarefas/` | responsavel |
| GET | `/tarefas/` | autenticado (filho vê só as suas) |
| GET | `/tarefas/{id}` | autenticado |
| PATCH | `/tarefas/{id}` | responsavel |
| DELETE | `/tarefas/{id}` | responsavel |
| POST | `/tarefas/{id}/concluir` | autenticado |
| POST | `/tarefas/{id}/aprovar` | responsavel |
| POST | `/tarefas/{id}/rejeitar` | responsavel |

Listagem aceita `?status_filtro=pendente&pagina=1&tamanho=20`.

### Recompensas (`/recompensas`)
CRUD completo. DELETE = desativação (soft delete). Leitura: autenticado.

### Metas (`/metas`)
CRUD completo. DELETE = cancelamento. Criação: responsavel.

### Resgates (`/resgates`)
| Método | Rota | Papel |
|---|---|---|
| POST | `/resgates/` | autenticado (debita pontos na hora) |
| GET | `/resgates/` | autenticado |
| PATCH | `/resgates/{id}` | responsavel (aprova/recusa/entrega) |

### Transações (`/transacoes`)
| Método | Rota | Papel |
|---|---|---|
| GET | `/transacoes/` | autenticado |
| POST | `/transacoes/bonus` | responsavel |

Aceita `?usuario_id=&pagina=&tamanho=`.

### Notificações (`/notificacoes`)
| Método | Rota |
|---|---|
| GET | `/notificacoes/?apenas_nao_lidas=false` |
| PATCH | `/notificacoes/{id}/lida` |
| POST | `/notificacoes/marcar-todas-lidas` |

## Lógica de negócio

### Fluxo de pontos
```
Tarefa criada (pendente)
  → Filho conclui (em_andamento)
    → Responsável aprova → creditar() + verificar_metas()
    → Responsável rejeita → notificação ao filho
```

### Verificação de metas
Ao aprovar uma tarefa, `verificar_metas()` percorre as metas ativas do filho, incrementa `pontos_atuais` e, se atingir `pontos_alvo`, concede o bônus de conclusão automaticamente.

### Fluxo de resgate
```
Filho solicita resgate → pontos debitados imediatamente → status: pendente
  → Responsável aprova/recusa/entrega
    → Se recusado: pontos estornados
```

### Tipos de notificação
`tarefa_atribuida` · `tarefa_concluida` · `tarefa_aprovada` · `tarefa_rejeitada` · `meta_atingida` · `resgate_aprovado`

## Frontend

### Rotas
| Rota | Papel | Tela |
|---|---|---|
| `/login` | público | Login |
| `/registro` | público | Cadastro |
| `/responsavel/dashboard` | responsavel | Dashboard com resumo |
| `/responsavel/tarefas` | responsavel | Gestão de tarefas |
| `/responsavel/recompensas` | responsavel | Gestão de recompensas |
| `/responsavel/membros` | responsavel | Membros da família |
| `/filho/dashboard` | filho | Pontos + tarefas pendentes |
| `/filho/tarefas` | filho | Lista de tarefas |
| `/filho/recompensas` | filho | Loja de recompensas |

### Arquitetura frontend
- `services/api.js` — instância Axios com interceptor JWT e auto-refresh
- `services/index.js` — todos os métodos de API organizados por domínio
- `stores/auth.js` — Pinia: login, logout, perfil
- `stores/notificacoes.js` — Pinia: lista e marcar lidas
- `router/index.js` — guards de navegação por papel

## Ordem de implementação

| Fase | Status | Conteúdo |
|---|---|---|
| 1 | ✅ | Setup do projeto, 9 modelos, autenticação JWT |
| 2 | ✅ | Todos os endpoints (tarefas, pontos, recompensas, metas, resgates, notificações) |
| 3 | ✅ | Categorias, paginação, testes pytest, scaffold frontend Vue 3 |
| 4 | 🔲 | Polish da interface do filho (acessibilidade), deploy |

## Como rodar localmente

```bash
# Backend
pip install -r requirements.txt
cp .env.example .env        # edite as variáveis
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Testes (criar banco specialpoints_test no pgAdmin antes)
pytest tests/ -v
```

Documentação interativa da API: `http://localhost:8000/docs`
