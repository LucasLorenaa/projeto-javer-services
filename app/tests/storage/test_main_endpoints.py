"""
Testes para storage/main.py com cobertura completa.
"""
import sys
from unittest.mock import patch, MagicMock, PropertyMock

# Mock jaydebeapi antes de qualquer import
sys.modules['jaydebeapi'] = MagicMock()

import pytest
from fastapi.testclient import TestClient

# Importar a app agora com jaydebeapi mockado
from storage.main import app


@pytest.fixture
def client():
    """Fixture para TestClient com aplicação storage."""
    return TestClient(app)


class TestStorageMainHealth:
    """Testes para o endpoint /health."""
    
    def test_health_success(self, client):
        """GET /health retorna status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "storage"}


class TestStorageMainListClients:
    """Testes para GET /clients."""
    
    @patch('storage.main.list_clients')
    def test_list_empty(self, mock_list, client):
        """Lista vazia retorna array vazio."""
        mock_list.return_value = []
        response = client.get("/clients")
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('storage.main.list_clients')
    def test_list_multiple(self, mock_list, client):
        """Lista com múltiplos clientes."""
        mock_data = [
            {
                "id": 1,
                "nome": "Alice",
                "telefone": 1190000000,
                "correntista": True,
                "score_credito": 100.0,
                "saldo_cc": 1000.0
            },
            {
                "id": 2,
                "nome": "Bob",
                "telefone": 1191111111,
                "correntista": False,
                "score_credito": None,
                "saldo_cc": None
            }
        ]
        mock_list.return_value = mock_data
        response = client.get("/clients")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nome"] == "Alice"
        assert data[1]["nome"] == "Bob"


class TestStorageMainGetClient:
    """Testes para GET /clients/{id}."""
    
    @patch('storage.main.get_client')
    def test_get_found(self, mock_get, client):
        """Cliente encontrado retorna dados."""
        mock_client = {
            "id": 1,
            "nome": "Alice",
            "telefone": 1190000000,
            "correntista": True,
            "score_credito": 100.0,
            "saldo_cc": 1000.0
        }
        mock_get.return_value = mock_client
        response = client.get("/clients/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["nome"] == "Alice"
    
    @patch('storage.main.get_client')
    def test_get_not_found(self, mock_get, client):
        """Cliente não encontrado retorna 404."""
        mock_get.return_value = None
        response = client.get("/clients/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()


class TestStorageMainCreateClient:
    """Testes para POST /clients."""
    
    @patch('storage.main.create_client')
    def test_create_success(self, mock_create, client):
        """Criação bem-sucedida retorna o cliente."""
        mock_created = {
            "id": 5,
            "nome": "Carol",
            "telefone": 1192222222,
            "correntista": True,
            "score_credito": 200.0,
            "saldo_cc": 2000.0
        }
        mock_create.return_value = mock_created
        payload = {
            "nome": "Carol",
            "telefone": 1192222222,
            "correntista": True,
            "score_credito": 200.0,
            "saldo_cc": 2000.0
        }
        response = client.post("/clients", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 5
        assert data["nome"] == "Carol"
    
    @patch('storage.main.create_client')
    def test_create_minimal(self, mock_create, client):
        """Criação com dados mínimos."""
        mock_created = {
            "id": 6,
            "nome": "Diana",
            "telefone": 1193333333,
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        mock_create.return_value = mock_created
        payload = {
            "nome": "Diana",
            "telefone": 1193333333,
            "correntista": False
        }
        response = client.post("/clients", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Diana"


class TestStorageMainUpdateClient:
    """Testes para PUT /clients/{id}."""
    
    @patch('storage.main.update_client')
    def test_update_found(self, mock_update, client):
        """Atualização bem-sucedida."""
        mock_updated = {
            "id": 1,
            "nome": "Alice Updated",
            "telefone": 1190000000,
            "correntista": False,
            "score_credito": 150.0,
            "saldo_cc": 1500.0
        }
        mock_update.return_value = mock_updated
        payload = {"nome": "Alice Updated", "correntista": False}
        response = client.put("/clients/1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Alice Updated"
    
    @patch('storage.main.update_client')
    def test_update_not_found(self, mock_update, client):
        """Atualizar cliente inexistente retorna 404."""
        mock_update.return_value = None
        response = client.put("/clients/999", json={"nome": "Ghost"})
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()
    
    @patch('storage.main.update_client')
    def test_update_partial(self, mock_update, client):
        """Atualização parcial de apenas alguns campos."""
        mock_updated = {
            "id": 2,
            "nome": "Bob",
            "telefone": 1191111111,
            "correntista": True,
            "score_credito": 250.0,
            "saldo_cc": 2500.0
        }
        mock_update.return_value = mock_updated
        payload = {"score_credito": 250.0, "saldo_cc": 2500.0}
        response = client.put("/clients/2", json=payload)
        assert response.status_code == 200


class TestStorageMainDeleteClient:
    """Testes para DELETE /clients/{id}."""
    
    @patch('storage.main.delete_client')
    def test_delete_found(self, mock_delete, client):
        """Deleção bem-sucedida retorna 204."""
        mock_delete.return_value = True
        response = client.delete("/clients/1")
        assert response.status_code == 204
        assert response.content == b""
    
    @patch('storage.main.delete_client')
    def test_delete_not_found(self, mock_delete, client):
        """Deletar cliente inexistente retorna 404."""
        mock_delete.return_value = False
        response = client.delete("/clients/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()
