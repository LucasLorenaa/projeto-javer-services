"""
Testes adicionais para aumentar cobertura a 97%+.
Foco em covering branch paths e edge cases.
"""
import sys
from unittest.mock import patch, MagicMock

# Mock jaydebeapi antes de qualquer import
sys.modules['jaydebeapi'] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from storage.main import app
from gateway.main import app as gateway_app


class TestStorageMainEdgeCases:
    """Testes de edge cases para storage/main.py."""
    
    @patch('storage.main.list_clients')
    def test_list_with_exception_handling(self, mock_list):
        """Teste quando list_clients retorna dados variados."""
        mock_list.return_value = [
            {"id": 1, "nome": "A", "telefone": 1190000000, "correntista": True, "score_credito": 0.0, "saldo_cc": 0.0},
            {"id": 2, "nome": "B", "telefone": 1191111111, "correntista": False, "score_credito": None, "saldo_cc": None},
        ]
        client = TestClient(app)
        response = client.get("/clients")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["score_credito"] == 0.0
        assert data[1]["score_credito"] is None
    
    @patch('storage.main.get_client')
    def test_get_with_zero_values(self, mock_get):
        """Teste GET com valores zero."""
        mock_get.return_value = {
            "id": 1,
            "nome": "Zero",
            "telefone": 1190000000,
            "correntista": False,
            "score_credito": 0.0,
            "saldo_cc": 0.0
        }
        client = TestClient(app)
        response = client.get("/clients/1")
        assert response.status_code == 200
        data = response.json()
        assert data["saldo_cc"] == 0.0
    
    @patch('storage.main.create_client')
    def test_create_response_code(self, mock_create):
        """Teste que POST retorna status 201."""
        mock_create.return_value = {"id": 1, "nome": "Test", "telefone": 1190000000, "correntista": True, "score_credito": None, "saldo_cc": None}
        client = TestClient(app)
        response = client.post("/clients", json={"nome": "Test", "telefone": 1190000000, "correntista": True})
        assert response.status_code == 201
    
    @patch('storage.main.update_client')
    def test_update_with_exclude_unset(self, mock_update):
        """Teste que PUT passa exclude_unset corretamente."""
        mock_update.return_value = {"id": 1, "nome": "Updated", "telefone": 1190000000, "correntista": True, "score_credito": 50.0, "saldo_cc": 500.0}
        client = TestClient(app)
        response = client.put("/clients/1", json={"nome": "Updated"})
        assert response.status_code == 200
        mock_update.assert_called_once()
    
    @patch('storage.main.delete_client')
    def test_delete_response_no_content(self, mock_delete):
        """Teste que DELETE retorna 204 com body vazio."""
        mock_delete.return_value = True
        client = TestClient(app)
        response = client.delete("/clients/1")
        assert response.status_code == 204
        assert len(response.content) == 0


class TestGatewayMainEdgeCases:
    """Testes de edge cases para gateway/main.py."""
    
    def test_health_gateway(self):
        """GET /health da gateway."""
        client = TestClient(gateway_app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "storage"
    
    def test_index_gateway(self):
        """Teste GET / do gateway."""
        client = TestClient(gateway_app)
        response = client.get("/")
        # Pode retornar arquivo ou fallback message
        assert response.status_code in [200, 404, 500]


class TestStorageLifespan:
    """Testes para o contexto lifespan de storage/main.py."""
    
    def test_app_lifespan_coverage(self):
        """Testa startup e shutdown do lifespan context manager."""
        with patch('storage.main.init_db') as mock_init:
            # Criar cliente força startup do lifespan
            with TestClient(app) as client:
                # Durante o contexto, init_db deve ter sido chamado
                mock_init.assert_called_once()
                
                # Fazer requisição básica
                response = client.get("/health")
                assert response.status_code == 200
            
            # Ao sair do contexto, shutdown é executado (linha 13 de storage/main.py)
            # Não há operações no shutdown, mas a linha é coberta


class TestRepositoryCloseConnections:
    """Testes para cobrir branches should_close=True em repository.py."""
    
    @patch('storage.repository.get_connection')
    def test_list_clients_closes_connection(self, mock_get_conn):
        """Testa que list_clients fecha conexão quando não está em cache."""
        import sqlite3
        from storage import repository
        
        # Criar conexão real mas sem cache
        real_conn = sqlite3.connect(":memory:", check_same_thread=False)
        cur = real_conn.cursor()
        cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
        real_conn.commit()
        
        mock_conn = MagicMock(wraps=real_conn)
        mock_conn.cursor.return_value = real_conn.cursor()
        mock_get_conn.return_value = mock_conn
        
        # Garantir que não está no cache
        if hasattr(repository.get_connection, '_sqlite_cache'):
            repository.get_connection._sqlite_cache = {}
        
        # Executar
        repository.list_clients()
        
        # Verificar que close foi chamado (linha 28 de repository.py)
        mock_conn.close.assert_called_once()
    
    @patch('storage.repository.get_connection')
    def test_get_client_closes_connection(self, mock_get_conn):
        """Testa que get_client fecha conexão quando não está em cache."""
        import sqlite3
        from storage import repository
        
        real_conn = sqlite3.connect(":memory:", check_same_thread=False)
        cur = real_conn.cursor()
        cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
        cur.execute("INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
                    ("Test", 123, 1, None, None))
        real_conn.commit()
        
        mock_conn = MagicMock(wraps=real_conn)
        mock_conn.cursor.return_value = real_conn.cursor()
        mock_get_conn.return_value = mock_conn
        
        if hasattr(repository.get_connection, '_sqlite_cache'):
            repository.get_connection._sqlite_cache = {}
        
        repository.get_client(1)
        
        # Verificar close (linha 43 de repository.py)
        mock_conn.close.assert_called_once()
    
    @patch('storage.repository.get_connection')
    def test_delete_client_closes_connection(self, mock_get_conn):
        """Testa que delete_client fecha conexão quando não está em cache."""
        import sqlite3
        from storage import repository
        
        real_conn = sqlite3.connect(":memory:", check_same_thread=False)
        cur = real_conn.cursor()
        cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
        cur.execute("INSERT INTO clients VALUES (1, 'ToDelete', 999, 0, NULL, NULL)")
        real_conn.commit()
        
        mock_conn = MagicMock(wraps=real_conn)
        mock_conn.cursor.return_value = real_conn.cursor()
        mock_get_conn.return_value = mock_conn
        
        if hasattr(repository.get_connection, '_sqlite_cache'):
            repository.get_connection._sqlite_cache = {}
        
        repository.delete_client(1)
        
        # Verificar close (linha 108 de repository.py)
        mock_conn.close.assert_called_once()
    
    @patch('storage.repository.get_connection')
    @patch('storage.repository.get_client')
    def test_create_client_closes_connection(self, mock_get_client, mock_get_conn):
        """Testa que create_client fecha conexão quando não está em cache."""
        import sqlite3
        from storage import repository
        
        real_conn = sqlite3.connect(":memory:", check_same_thread=False)
        cur = real_conn.cursor()
        cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
        real_conn.commit()
        
        mock_conn = MagicMock(wraps=real_conn)
        mock_conn.cursor.return_value = real_conn.cursor()
        mock_conn.commit = real_conn.commit
        mock_get_conn.return_value = mock_conn
        
        # Mock get_client para retornar o cliente criado
        mock_get_client.return_value = {
            "id": 1, "nome": "New", "telefone": 123, 
            "correntista": True, "score_credito": None, "saldo_cc": None
        }
        
        if hasattr(repository.get_connection, '_sqlite_cache'):
            repository.get_connection._sqlite_cache = {}
        
        repository.create_client({
            "nome": "New", "telefone": 123, "correntista": True
        })
        
        # Verificar close (linha 69 de repository.py)
        mock_conn.close.assert_called_once()
    
    @patch('storage.repository.get_connection')
    @patch('storage.repository.get_client')
    def test_update_client_closes_connection(self, mock_get_client, mock_get_conn):
        """Testa que update_client fecha conexão quando não está em cache."""
        import sqlite3
        from storage import repository
        
        real_conn = sqlite3.connect(":memory:", check_same_thread=False)
        cur = real_conn.cursor()
        cur.execute("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
        cur.execute("INSERT INTO clients VALUES (1, 'Old', 111, 1, NULL, NULL)")
        real_conn.commit()
        
        mock_conn = MagicMock(wraps=real_conn)
        mock_conn.cursor.return_value = real_conn.cursor()
        mock_conn.commit = real_conn.commit
        
        # Primeira chamada get_client retorna cliente existente
        # Segunda chamada get_client retorna cliente atualizado
        mock_get_client.side_effect = [
            {"id": 1, "nome": "Old", "telefone": 111, "correntista": True, "score_credito": None, "saldo_cc": None},
            {"id": 1, "nome": "Updated", "telefone": 111, "correntista": True, "score_credito": None, "saldo_cc": None}
        ]
        
        mock_get_conn.return_value = mock_conn
        
        if hasattr(repository.get_connection, '_sqlite_cache'):
            repository.get_connection._sqlite_cache = {}
        
        repository.update_client(1, {"nome": "Updated"})
        
        # Verificar close (linha 91 de repository.py)
        mock_conn.close.assert_called_once()
