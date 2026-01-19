import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from storage.main import app


client = TestClient(app)


# ===== GET /health =====
def test_health_storage():
    """Testa health check do storage"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "storage"}


# ===== GET /clients =====
@patch("storage.main.list_clients")
def test_list_clients_storage(mock_list):
    """Testa listar clientes do storage"""
    mock_list.return_value = [
        {"id": 1, "nome": "João", "email": "joao@test.com", "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None},
        {"id": 2, "nome": "Maria", "email": "maria@test.com", "data_nascimento": "2000-01-02", "telefone": 987654321, "correntista": False, "score_credito": None, "saldo_cc": None},
    ]
    
    response = client.get("/clients")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@patch("storage.main.list_clients")
def test_list_clients_storage_vazio(mock_list):
    """Testa listar clientes quando lista está vazia"""
    mock_list.return_value = []
    
    response = client.get("/clients")
    assert response.status_code == 200
    assert response.json() == []


# ===== GET /clients/{client_id} =====
@patch("storage.main.get_client")
def test_get_client_storage_sucesso(mock_get):
    """Testa buscar cliente do storage por ID"""
    mock_get.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None
    }
    
    response = client.get("/clients/1")
    assert response.status_code == 200
    assert response.json()["nome"] == "João"


@patch("storage.main.get_client")
def test_get_client_storage_nao_encontrado(mock_get):
    """Testa buscar cliente inexistente"""
    mock_get.return_value = None
    
    response = client.get("/clients/999")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


# ===== POST /clients =====
@patch("storage.main.create_client")
def test_create_client_storage_sucesso(mock_create):
    """Testa criar cliente no storage"""
    mock_create.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None
    }
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] == 1


@patch("storage.main.create_client")
def test_create_client_storage_erro_validacao(mock_create):
    """Testa criar cliente com erro de validação"""
    mock_create.side_effect = ValueError("Email já existe")
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 400
    assert "Email já existe" in response.json()["detail"]


# ===== POST /register =====
@patch("storage.main.create_client")
def test_register_storage_sucesso(mock_create):
    """Testa registro de novo cliente no storage"""
    mock_create.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None
    }
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201


@patch("storage.main.create_client")
def test_register_storage_erro_validacao(mock_create):
    """Testa registro com erro de validação"""
    mock_create.side_effect = ValueError("Email já existe")
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


# ===== POST /login =====
@patch("storage.main.login_client")
def test_login_storage_sucesso(mock_login):
    """Testa login no storage com sucesso"""
    mock_login.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None
    }
    
    payload = {"email": "joao@test.com", "senha": "senhaSegura123!"}
    response = client.post("/login", json=payload)
    assert response.status_code == 200


@patch("storage.main.login_client")
def test_login_storage_falha(mock_login):
    """Testa login com falha (credenciais inválidas)"""
    mock_login.return_value = None
    
    payload = {"email": "joao@test.com", "senha": "senhaErrada"}
    response = client.post("/login", json=payload)
    assert response.status_code == 401
    assert "inválidos" in response.json()["detail"]


# ===== PUT /clients/{client_id} =====
@patch("storage.main.update_client")
def test_update_client_storage_sucesso(mock_update):
    """Testa atualizar cliente no storage"""
    mock_update.return_value = {
        "id": 1, "nome": "João Atualizado", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "telefone": 123456789, "correntista": True, "score_credito": None, "saldo_cc": None
    }
    
    payload = {"nome": "João Atualizado"}
    response = client.put("/clients/1", json=payload)
    assert response.status_code == 200
    assert response.json()["nome"] == "João Atualizado"


@patch("storage.main.update_client")
def test_update_client_storage_nao_encontrado(mock_update):
    """Testa atualizar cliente inexistente"""
    mock_update.return_value = None
    
    payload = {"nome": "João Atualizado"}
    response = client.put("/clients/999", json=payload)
    assert response.status_code == 404


@patch("storage.main.update_client")
def test_update_client_storage_erro_validacao(mock_update):
    """Testa atualizar cliente com erro de validação"""
    mock_update.side_effect = ValueError("Dados inválidos")
    
    payload = {"nome": "João Atualizado"}
    response = client.put("/clients/1", json=payload)
    assert response.status_code == 400


# ===== DELETE /clients/{client_id} =====
@patch("storage.main.delete_client")
def test_delete_client_storage_sucesso(mock_delete):
    """Testa deletar cliente do storage"""
    mock_delete.return_value = True
    
    response = client.delete("/clients/1")
    assert response.status_code == 204


@patch("storage.main.delete_client")
def test_delete_client_storage_nao_encontrado(mock_delete):
    """Testa deletar cliente inexistente"""
    mock_delete.return_value = False
    
    response = client.delete("/clients/999")
    assert response.status_code == 404


# ===== PUT /password =====
@patch("storage.main.update_password")
def test_update_password_storage_sucesso(mock_update_pass):
    """Testa atualizar senha no storage"""
    mock_update_pass.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    
    payload = {"email": "joao@test.com", "senha_atual": "antiga", "senha_nova": "novaSegura123!"}
    response = client.put("/password", json=payload)
    assert response.status_code == 200


# Testes de validação (request validation)
def test_register_validacao_email_invalido():
    """Testa validação de email no registro"""
    payload = {
        "nome": "João",
        "email": "invalid-email",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_register_validacao_idade_minima():
    """Testa validação de idade mínima no registro"""
    from datetime import datetime, timedelta
    data_invalida = (datetime.now() - timedelta(days=365*17)).strftime("%Y-%m-%d")
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": data_invalida,
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_register_validacao_senha_curta():
    """Testa validação de senha mínima no registro"""
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_login_validacao_email_obrigatorio():
    """Testa validação de email obrigatório no login"""
    payload = {"senha": "senhaSegura123!"}
    response = client.post("/login", json=payload)
    assert response.status_code == 422


def test_create_client_validacao_email_invalido():
    """Testa validação de email na criação"""
    payload = {
        "nome": "João",
        "email": "invalid-email",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 422
