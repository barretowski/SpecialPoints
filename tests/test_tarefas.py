import pytest
from httpx import AsyncClient


async def _registrar_e_logar(client: AsyncClient, email: str, papel: str, familia_nome: str | None = None, familia_codigo: str | None = None) -> str:
    await client.post("/auth/registro", json={
        "nome": "Usuário",
        "email": email,
        "senha": "senha123",
        "papel": papel,
        "familia_nome": familia_nome,
        "familia_codigo": familia_codigo,
    })
    resp = await client.post("/auth/login", json={"email": email, "senha": "senha123"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_criar_tarefa(client: AsyncClient):
    token = await _registrar_e_logar(client, "resp1@test.com", "responsavel", familia_nome="Família 1")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/tarefas/", headers=headers, json={
        "titulo": "Lavar a louça",
        "pontos": 10,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["titulo"] == "Lavar a louça"
    assert data["pontos"] == 10
    assert data["status"] == "pendente"


@pytest.mark.asyncio
async def test_filho_nao_pode_criar_tarefa(client: AsyncClient):
    token = await _registrar_e_logar(client, "filho1@test.com", "filho", familia_nome="Família Filho1")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/tarefas/", headers=headers, json={
        "titulo": "Tarefa indevida",
        "pontos": 5,
    })
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_fluxo_completo_tarefa(client: AsyncClient):
    # Responsável cria família e tarefa
    token_resp = await _registrar_e_logar(client, "resp2@test.com", "responsavel", familia_nome="Família 2")
    headers_resp = {"Authorization": f"Bearer {token_resp}"}

    me = await client.get("/auth/me", headers=headers_resp)
    familia_id = me.json()["familia_id"]

    # Busca código de convite listando membros (simplificado: registra filho na mesma família)
    # Para o teste, vamos usar o responsável como "atribuído" (simplificado)
    resp_tarefa = await client.post("/tarefas/", headers=headers_resp, json={
        "titulo": "Varrer o quintal",
        "pontos": 20,
    })
    assert resp_tarefa.status_code == 201
    tarefa_id = resp_tarefa.json()["id"]

    # Lista tarefas
    resp_lista = await client.get("/tarefas/", headers=headers_resp)
    assert resp_lista.status_code == 200
    assert any(t["id"] == tarefa_id for t in resp_lista.json())

    # Responsável conclui a própria tarefa (sem filho atribuído)
    resp_conclui = await client.post(f"/tarefas/{tarefa_id}/concluir", headers=headers_resp)
    assert resp_conclui.status_code == 200
    assert resp_conclui.json()["status"] == "em_andamento"


@pytest.mark.asyncio
async def test_paginacao_tarefas(client: AsyncClient):
    token = await _registrar_e_logar(client, "resp3@test.com", "responsavel", familia_nome="Família 3")
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(5):
        await client.post("/tarefas/", headers=headers, json={"titulo": f"Tarefa {i}", "pontos": 5})

    resp = await client.get("/tarefas/?pagina=1&tamanho=3", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) <= 3
