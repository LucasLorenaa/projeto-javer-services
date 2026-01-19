"""Testes para cobrir gaps de cobertura no gateway (97% -> 100%)."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from gateway.main import app
from gateway import client as client_module
import httpx


client = TestClient(app)


# ===== Tests for login with unhandled HTTPStatusError =====
@patch("gateway.main.get_dynamic_http_client")
def test_login_http_status_error_500(mock_get_client):
    """Testa login com HTTPStatusError 500 (não é 401, deve propagar)"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.post.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha": "senhaErrada"}
    with pytest.raises(httpx.HTTPStatusError):
        client.post("/login", json=payload)


# ===== Tests for post_login function in client module =====
def test_post_login_success():
    """Testa função post_login do módulo client"""
    with patch("gateway.client.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1, "nome": "João", "email": "joao@test.com",
            "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": None
        }
        mock_client_instance.post.return_value = mock_response
        
        result = client_module.post_login("joao@test.com", "senha123")
        assert result.json()["id"] == 1


def test_post_login_invalid_credentials():
    """Testa post_login com credenciais inválidas"""
    with patch("gateway.client.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Email ou senha inválidos"}
        mock_client_instance.post.return_value = mock_response
        
        result = client_module.post_login("joao@test.com", "senhaErrada")
        assert result.status_code == 401


# ===== Tests for frontend pages when files don't exist =====
@patch("gateway.main.Path.exists")
def test_index_page_not_found(mock_exists):
    """Testa index page quando arquivo não existe"""
    mock_exists.return_value = False
    
    response = client.get("/")
    assert response.status_code == 200
    assert "não disponível" in response.json()["message"]


@patch("gateway.main.Path.exists")
def test_login_page_html_not_found(mock_exists):
    """Testa login.html quando arquivo não existe"""
    mock_exists.return_value = False
    
    response = client.get("/login.html")
    assert response.status_code == 200
    assert "não disponível" in response.json()["message"]


@patch("gateway.main.Path.exists")
def test_register_page_html_not_found(mock_exists):
    """Testa register.html quando arquivo não existe"""
    mock_exists.return_value = False
    
    response = client.get("/register.html")
    assert response.status_code == 200
    assert "não disponível" in response.json()["message"]


@patch("gateway.main.Path.exists")
def test_response_page_not_found(mock_exists):
    """Testa response page quando arquivo não existe"""
    mock_exists.return_value = False
    
    response = client.get("/response")
    assert response.status_code == 200
    assert "não disponível" in response.json()["message"]


@patch("gateway.main.Path.exists")
def test_dashboard_page_not_found(mock_exists):
    """Testa dashboard page quando arquivo não existe"""
    mock_exists.return_value = False
    
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "não disponível" in response.json()["message"]


# ===== Additional edge case tests =====
@patch("gateway.main.get_dynamic_http_client")
def test_create_client_http_error_generic(mock_get_client):
    """Testa criar cliente com erro HTTP genérico"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.post.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    with pytest.raises(httpx.HTTPStatusError):
        client.post("/clients", json=payload)


@patch("gateway.main.get_dynamic_http_client")
def test_register_http_error_generic(mock_get_client):
    """Testa registro com erro HTTP genérico"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.post.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {
        "nome": "João",
        "email": "joao@test.com",
        "data_nascimento": "2000-01-01",
        "senha": "senhaSegura123!"
    }
    with pytest.raises(httpx.HTTPStatusError):
        client.post("/register", json=payload)


@patch("gateway.main.get_dynamic_http_client")
def test_update_password_http_error_generic(mock_get_client):
    """Testa atualizar senha com erro HTTP genérico"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.put.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {"email": "joao@test.com", "senha_atual": "antiga", "senha_nova": "novaSegura123!"}
    with pytest.raises(httpx.HTTPStatusError):
        client.put("/password", json=payload)


@patch("gateway.main.get_dynamic_http_client")
def test_list_clients_error(mock_get_client):
    """Testa listar clientes com erro HTTP"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.get.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    with pytest.raises(httpx.HTTPStatusError):
        client.get("/clients")


@patch("gateway.main.get_dynamic_http_client")
def test_get_client_error(mock_get_client):
    """Testa obter cliente com erro HTTP"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.get.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    with pytest.raises(httpx.HTTPStatusError):
        client.get("/clients/1")


@patch("gateway.main.get_dynamic_http_client")
def test_delete_client_error(mock_get_client):
    """Testa deletar cliente com erro HTTP"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.delete.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    with pytest.raises(httpx.HTTPStatusError):
        client.delete("/clients/1")


@patch("gateway.main.get_dynamic_http_client")
def test_update_client_error(mock_get_client):
    """Testa atualizar cliente com erro HTTP"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.put.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    payload = {"nome": "João Atualizado"}
    with pytest.raises(httpx.HTTPStatusError):
        client.put("/clients/1", json=payload)


@patch("gateway.main.get_dynamic_http_client")
def test_score_credito_error(mock_get_client):
    """Testa score de crédito com erro HTTP"""
    mock_http_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 500
    error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
    mock_http_client.get.side_effect = error
    mock_get_client.return_value = mock_http_client
    
    with pytest.raises(httpx.HTTPStatusError):
        client.get("/clients/1/score")
