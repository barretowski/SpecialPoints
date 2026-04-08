import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_registro_responsavel(client: AsyncClient):
    resp = await client.post("/auth/registro", json={
        "nome": "Maria",
        "email": "maria@exemplo.com",
        "senha": "senha123",
        "papel": "responsavel",
        "familia_nome": "Família Silva",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "maria@exemplo.com"
    assert data["papel"] == "responsavel"
    assert data["pontos_disponiveis"] == 0


@pytest.mark.asyncio
async def test_registro_email_duplicado(client: AsyncClient):
    payload = {
        "nome": "Joao",
        "email": "joao@exemplo.com",
        "senha": "senha123",
        "papel": "responsavel",
        "familia_nome": "Família Joao",
    }
    await client.post("/auth/registro", json=payload)
    resp = await client.post("/auth/registro", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient):
    await client.post("/auth/registro", json={
        "nome": "Ana",
        "email": "ana@exemplo.com",
        "senha": "senha123",
        "papel": "responsavel",
        "familia_nome": "Família Ana",
    })
    resp = await client.post("/auth/login", json={"email": "ana@exemplo.com", "senha": "senha123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_senha_errada(client: AsyncClient):
    await client.post("/auth/registro", json={
        "nome": "Pedro",
        "email": "pedro@exemplo.com",
        "senha": "certa123",
        "papel": "responsavel",
        "familia_nome": "Família Pedro",
    })
    resp = await client.post("/auth/login", json={"email": "pedro@exemplo.com", "senha": "errada"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_autenticado(client: AsyncClient, responsavel_token: str):
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {responsavel_token}"})
    assert resp.status_code == 200
    assert resp.json()["papel"] == "responsavel"


@pytest.mark.asyncio
async def test_me_sem_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 403
