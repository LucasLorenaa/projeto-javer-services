import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from gateway.main import app
from gateway.models import ClientCreate, ClientUpdate, ClientOut, ClientRegister, ClientLogin, ClientPasswordReset
import httpx


client = TestClient(app)


# ===== GET / (Index) =====
def test_index_arquivo_existe():
    """Testa retorno da página inicial quando arquivo existe"""
    response = client.get("/")
    assert response.status_code == 200


# ===== GET /login.html =====
def test_login_page_html():
    """Testa retorno da página login.html"""
    response = client.get("/login.html")
    assert response.status_code == 200


# ===== GET /login =====
def test_login_page():
    """Testa retorno da página /login"""
    response = client.get("/login")
    assert response.status_code == 200


# ===== GET /register.html =====
def test_register_page_html():
    """Testa retorno da página register.html"""
    response = client.get("/register.html")
    assert response.status_code == 200


# ===== GET /register (página) =====
def test_register_page():
    """Testa retorno da página /register"""
    response = client.get("/register")
    assert response.status_code == 200


# ===== GET /response =====
def test_response_page():
    """Testa retorno da página /response"""
    response = client.get("/response")
    assert response.status_code == 200


# ===== GET /dashboard =====
def test_dashboard_page():
    """Testa retorno da página /dashboard"""
    response = client.get("/dashboard")
    assert response.status_code == 200


# ===== GET /health =====
def test_health():
    """Testa endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "gateway"}


# ===== GET /clients (list) =====
@patch("gateway.main.get_dynamic_http_client")
def test_list_clients_sucesso(mock_get_client):
    """Testa listar clientes com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "nome": "João", "email": "joao@test.com", "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None},
        {"id": 2, "nome": "Maria", "email": "maria@test.com", "data_nascimento": "2000-01-02", "score_credito": None, "saldo_cc": None},
    ]
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nome"] == "João"


@patch("gateway.main.get_dynamic_http_client")
def test_list_clients_erro_status(mock_get_client):
    """Testa erro ao listar clientes"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    with pytest.raises(Exception):
        client.get("/clients")


# ===== GET /clients/{client_id} =====
@patch("gateway.main.get_dynamic_http_client")
def test_get_client_sucesso(mock_get_client):
    """Testa buscar cliente por ID com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com", 
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients/1")
    assert response.status_code == 200
    assert response.json()["nome"] == "João"


@patch("gateway.main.get_dynamic_http_client")
def test_get_client_nao_encontrado(mock_get_client):
    """Testa buscar cliente inexistente (404)"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients/999")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


# ===== POST /clients =====
@patch("gateway.main.get_dynamic_http_client")
def test_create_client_sucesso(mock_get_client):
    """Testa criar cliente com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.post.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/clients", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] == 1


@patch("gateway.main.get_dynamic_http_client")
def test_create_client_validacao_fallha(mock_get_client):
    """Testa criar cliente com email inválido"""
    response = client.post("/clients", json={
        "nome": "João",
        "email": "email-invalido",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    })
    assert response.status_code == 422


# ===== POST /register (API) =====
@patch("gateway.main.get_dynamic_http_client")
def test_register_sucesso(mock_get_client):
    """Testa registro de novo cliente com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.post.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201


@patch("gateway.main.get_dynamic_http_client")
def test_register_erro_400(mock_get_client):
    """Testa registro com erro 400 (email duplicado)"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Email já existe"}
    mock_http_client.post.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert "Email já existe" in response.json()["detail"]


@patch("gateway.main.get_dynamic_http_client")
def test_register_http_status_error(mock_get_client):
    """Testa register com HTTPStatusError 400"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Erro genérico"}
    error = httpx.HTTPStatusError("400", request=Mock(), response=mock_response)
    mock_http_client.post.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


# ===== POST /login (API) =====
@patch("gateway.main.get_dynamic_http_client")
def test_login_sucesso(mock_get_client):
    """Testa login com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.post.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha": "senhaSegura123!"}
    response = client.post("/login", json=payload)
    assert response.status_code == 200


@patch("gateway.main.get_dynamic_http_client")
def test_login_credenciais_invalidas(mock_get_client):
    """Testa login com credenciais inválidas (401)"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 401
    mock_http_client.post.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha": "senhaErrada"}
    response = client.post("/login", json=payload)
    assert response.status_code == 401
    assert "inválidos" in response.json()["detail"]


@patch("gateway.main.get_dynamic_http_client")
def test_login_http_status_error_401(mock_get_client):
    """Testa login com HTTPStatusError 401"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 401
    error = httpx.HTTPStatusError("401", request=Mock(), response=mock_response)
    mock_http_client.post.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha": "senhaErrada"}
    response = client.post("/login", json=payload)
    assert response.status_code == 401


# ===== PUT /clients/{client_id} =====
@patch("gateway.main.get_dynamic_http_client")
def test_update_client_sucesso(mock_get_client):
    """Testa atualizar cliente com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João Atualizado", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.put.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"nome": "João Atualizado"}
    response = client.put("/clients/1", json=payload)
    assert response.status_code == 200
    assert response.json()["nome"] == "João Atualizado"


@patch("gateway.main.get_dynamic_http_client")
def test_update_client_nao_encontrado(mock_get_client):
    """Testa atualizar cliente inexistente"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_client.put.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"nome": "João Atualizado"}
    response = client.put("/clients/999", json=payload)
    assert response.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
def test_update_client_com_data(mock_get_client):
    """Testa atualizar cliente com data_nascimento"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.put.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"data_nascimento": "2000-01-01"}
    response = client.put("/clients/1", json=payload)
    assert response.status_code == 200


# ===== DELETE /clients/{client_id} =====
@patch("gateway.main.get_dynamic_http_client")
def test_delete_client_sucesso(mock_get_client):
    """Testa deletar cliente com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 204
    mock_http_client.delete.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.delete("/clients/1")
    assert response.status_code == 204


@patch("gateway.main.get_dynamic_http_client")
def test_delete_client_nao_encontrado(mock_get_client):
    """Testa deletar cliente inexistente"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_client.delete.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.delete("/clients/999")
    assert response.status_code == 404


# ===== PUT /password =====
@patch("gateway.main.get_dynamic_http_client")
def test_update_password_sucesso(mock_get_client):
    """Testa atualizar senha com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.put.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha_atual": "antiga", "senha_nova": "novaSegura123!"}
    response = client.put("/password", json=payload)
    assert response.status_code == 200


@patch("gateway.main.get_dynamic_http_client")
def test_update_password_cliente_nao_encontrado(mock_get_client):
    """Testa atualizar senha de cliente inexistente"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_client.put.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "inexistente@test.com", "senha_atual": "antiga", "senha_nova": "novaSegura123!"}
    response = client.put("/password", json=payload)
    assert response.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
def test_update_password_http_error_404(mock_get_client):
    """Testa atualizar senha com HTTPStatusError 404"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
    mock_http_client.put.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "inexistente@test.com", "senha_atual": "antiga", "senha_nova": "novaSegura123!"}
    response = client.put("/password", json=payload)
    assert response.status_code == 404


# ===== GET /clients/{client_id}/score =====
@patch("gateway.main.get_dynamic_http_client")
def test_score_credito_sucesso(mock_get_client):
    """Testa calcular score de crédito com sucesso"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": 100, "saldo_cc": 1000
    }
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients/1/score")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["score_calculado"] == 100  # saldo 1000 * 0.1


@patch("gateway.main.get_dynamic_http_client")
def test_score_credito_saldo_nulo(mock_get_client):
    """Testa score de crédito quando saldo é nulo"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "nome": "João", "email": "joao@test.com",
        "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
    }
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients/1/score")
    assert response.status_code == 200
    data = response.json()
    assert data["score_calculado"] is None


@patch("gateway.main.get_dynamic_http_client")
def test_score_credito_cliente_nao_encontrado(mock_get_client):
    """Testa score de cliente inexistente"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_http_client.get.return_value = mock_response
    mock_get_client.return_value = mock_http_client
    
    response = client.get("/clients/999/score")
    assert response.status_code == 404
