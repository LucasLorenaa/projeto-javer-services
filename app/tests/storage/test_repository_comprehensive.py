"""Comprehensive unit tests for storage repository with data_nascimento"""
import pytest
from datetime import date
from unittest.mock import Mock, MagicMock, patch
from storage.repository import (
    create_client,
    get_client,
    list_clients,
    update_client,
    delete_client,
    login_client,
    _row_to_client
)


@pytest.fixture
def mock_connection():
    """Mock database connection"""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = None
    return conn


@pytest.fixture
def sample_client_row():
    """Sample client row from database (8 fields)"""
    return (
        1,                          # id
        "João Silva",               # nome
        21999999999,                # telefone
        "joao@test.com",            # email
        date(1990, 5, 15),          # data_nascimento
        False,                      # correntista
        None,                       # score_credito
        None                        # saldo_cc
    )


@pytest.fixture
def sample_client_dict():
    """Sample client as dict"""
    return {
        "id": 1,
        "nome": "João Silva",
        "telefone": 21999999999,
        "email": "joao@test.com",
        "data_nascimento": "1990-05-15",
        "correntista": False,
        "score_credito": None,
        "saldo_cc": None
    }


class TestRowToClient:
    """Test _row_to_client helper function"""
    
    def test_row_to_client_basic(self, sample_client_row):
        """Test basic row conversion"""
        result = _row_to_client(sample_client_row)
        assert result["id"] == 1
        assert result["nome"] == "João Silva"
        assert result["email"] == "joao@test.com"
        assert result["telefone"] == 21999999999
        assert result["data_nascimento"] == date(1990, 5, 15)
        assert result["correntista"] is False
        assert result["score_credito"] is None
        assert result["saldo_cc"] is None

    def test_row_to_client_with_financial_data(self):
        """Test row conversion with financial data"""
        row = (
            2,                          # id
            "Maria Santos",             # nome
            21988888888,                # telefone
            "maria@test.com",           # email
            date(1985, 3, 20),          # data_nascimento
            True,                       # correntista
            850.5,                      # score_credito
            15000.0                     # saldo_cc
        )
        result = _row_to_client(row)
        assert result["id"] == 2
        assert result["correntista"] is True
        assert result["score_credito"] == 850.5
        assert result["saldo_cc"] == 15000.0
        assert result["data_nascimento"] == date(1985, 3, 20)

    def test_row_to_client_preserves_date_format(self):
        """Test date format preservation"""
        row = (1, "Test", 21999999999, "test@test.com", date(2000, 1, 1), False, None, None)
        result = _row_to_client(row)
        assert result["data_nascimento"] == date(2000, 1, 1)


class TestCreateClient:
    """Test create_client function"""
    
    @patch('storage.repository._ensure_unique')
    @patch('storage.repository.get_connection')
    def test_create_client_success(self, mock_get_conn, mock_ensure_unique, mock_connection, sample_client_row):
        """Test successful client creation"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = sample_client_row
        mock_ensure_unique.return_value = None  # No conflict
        
        client_data = {
            "nome": "João Silva",
            "telefone": 21999999999,
            "email": "joao@test.com",
            "data_nascimento": date(1990, 5, 15),
            "senha_hash": "hashed_password",
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        
        result = create_client(client_data)
        assert result["id"] == 1
        assert result["nome"] == "João Silva"
        assert result["email"] == "joao@test.com"
        assert result["data_nascimento"] == date(1990, 5, 15)

    @patch('storage.repository._ensure_unique')
    @patch('storage.repository.get_connection')
    def test_create_client_with_optional_fields(self, mock_get_conn, mock_ensure_unique, mock_connection):
        """Test creating client with optional financial fields"""
        row = (3, "Pedro", 21977777777, "pedro@test.com", date(1992, 10, 5), True, 750.0, 5000.0)
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = row
        mock_ensure_unique.return_value = None
        
        client_data = {
            "nome": "Pedro",
            "telefone": 21977777777,
            "email": "pedro@test.com",
            "data_nascimento": date(1992, 10, 5),
            "senha_hash": "hash",
            "correntista": True,
            "score_credito": 750.0,
            "saldo_cc": 5000.0
        }
        
        result = create_client(client_data)
        assert result["correntista"] is True
        assert result["score_credito"] == 750.0
        assert result["saldo_cc"] == 5000.0


class TestGetClient:
    """Test get_client function"""
    
    @patch('storage.repository.get_connection')
    def test_get_client_found(self, mock_get_conn, mock_connection, sample_client_row):
        """Test retrieving existing client"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = sample_client_row
        
        result = get_client(1)
        assert result is not None
        assert result["id"] == 1
        assert result["email"] == "joao@test.com"
        assert result["data_nascimento"] == date(1990, 5, 15)

    @patch('storage.repository.get_connection')
    def test_get_client_not_found(self, mock_get_conn, mock_connection):
        """Test retrieving non-existent client"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = None
        
        result = get_client(999)
        assert result is None


class TestListClients:
    """Test list_clients function"""
    
    @patch('storage.repository.get_connection')
    def test_list_clients_multiple(self, mock_get_conn, mock_connection):
        """Test listing multiple clients"""
        rows = [
            (1, "User1", 21999999999, "user1@test.com", date(1990, 1, 1), False, None, None),
            (2, "User2", 21988888888, "user2@test.com", date(1985, 5, 15), True, 800.0, 10000.0)
        ]
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchall.return_value = rows
        
        result = list_clients()
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert result[1]["correntista"] is True

    @patch('storage.repository.get_connection')
    def test_list_clients_empty(self, mock_get_conn, mock_connection):
        """Test listing when no clients exist"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchall.return_value = []
        
        result = list_clients()
        assert result == []


class TestUpdateClient:
    """Test update_client function"""
    
    @patch('storage.repository._ensure_unique')
    @patch('storage.repository.get_client')
    @patch('storage.repository.get_connection')
    def test_update_client_basic_fields(self, mock_get_conn, mock_get_client, mock_ensure_unique, mock_connection):
        """Test updating basic client fields"""
        # Mock get_client to return different values on successive calls
        old_client = {
            "id": 1,
            "nome": "Old Name",
            "email": "old@test.com",
            "telefone": 21999999999,
            "data_nascimento": date(1990, 5, 15),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        
        updated_client = {
            "id": 1,
            "nome": "Updated Name",
            "email": "new@test.com",
            "telefone": 21977777777,
            "data_nascimento": date(1990, 5, 15),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        
        # First call returns old, second call returns updated
        mock_get_client.side_effect = [old_client, updated_client]
        mock_ensure_unique.return_value = None
        
        # Mock connection and hash query
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = ("current_hash",)
        
        update_data = {
            "nome": "Updated Name",
            "email": "new@test.com",
            "telefone": 21977777777
        }
        
        result = update_client(1, update_data)
        assert result["nome"] == "Updated Name"
        assert result["email"] == "new@test.com"

    @patch('storage.repository._ensure_unique')
    @patch('storage.repository.get_client')
    @patch('storage.repository.get_connection')
    def test_update_client_preserves_password(self, mock_get_conn, mock_get_client, mock_ensure_unique, mock_connection):
        """Test that update preserves password when not provided"""
        mock_get_client.return_value = {
            "id": 1,
            "nome": "User",
            "email": "user@test.com",
            "telefone": 21999999999,
            "data_nascimento": date(1990, 1, 1),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        
        mock_ensure_unique.return_value = None
        
        # Mock hash preservation
        final_row = (1, "User", 21999999999, "newemail@test.com", date(1990, 1, 1), False, None, None)
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.side_effect = [
            ("original_hash",),  # Hash retrieval
            final_row            # Final client
        ]
        
        update_data = {"email": "newemail@test.com"}
        result = update_client(1, update_data)
        
        # Verify hash was queried
        assert mock_connection.cursor.return_value.execute.call_count >= 2

    @patch('storage.repository._ensure_unique')
    @patch('storage.repository.get_client')
    @patch('storage.repository.get_connection')
    def test_update_client_with_password(self, mock_get_conn, mock_get_client, mock_ensure_unique, mock_connection):
        """Test updating password explicitly"""
        mock_get_client.return_value = {
            "id": 1,
            "nome": "User",
            "email": "user@test.com",
            "telefone": 21999999999,
            "data_nascimento": date(1990, 1, 1),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        
        mock_ensure_unique.return_value = None
        
        final_row = (1, "User", 21999999999, "user@test.com", date(1990, 1, 1), False, None, None)
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.side_effect = [
            ("old_hash",),
            final_row
        ]
        
        update_data = {"senha_hash": "new_hash"}
        result = update_client(1, update_data)
        assert result is not None


class TestDeleteClient:
    """Test delete_client function"""
    
    @patch('storage.repository.get_connection')
    def test_delete_client_success(self, mock_get_conn, mock_connection):
        """Test successful client deletion"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.rowcount = 1
        
        result = delete_client(1)
        assert result is True

    @patch('storage.repository.get_connection')
    def test_delete_client_not_found(self, mock_get_conn, mock_connection):
        """Test deleting non-existent client"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.rowcount = 0
        
        result = delete_client(999)
        assert result is False


class TestLoginClient:
    """Test login_client function"""
    
    @patch('storage.repository._verify_password')
    @patch('storage.repository.get_connection')
    def test_login_client_success(self, mock_get_conn, mock_verify, mock_connection, sample_client_row):
        """Test successful login"""
        # Add senha_hash to row (9 fields for login query)
        # Using valid bcrypt hash format
        login_row = sample_client_row + ("$2b$12$somevalidhashlookalike",)
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = login_row
        mock_verify.return_value = True  # Password verified
        
        result = login_client("joao@test.com", "password123")
        assert result is not None
        assert result["email"] == "joao@test.com"
        assert result["data_nascimento"] == date(1990, 5, 15)

    @patch('storage.repository.get_connection')
    def test_login_client_not_found(self, mock_get_conn, mock_connection):
        """Test login with non-existent email"""
        mock_get_conn.return_value = mock_connection
        mock_connection.cursor.return_value.fetchone.return_value = None
        
        result = login_client("nonexistent@test.com", "password")
        assert result is None
