import sqlite3
from unittest.mock import patch, MagicMock
import pytest
from storage import repository


def create_mock_conn_with_data(data_rows=None):
    """Cria um mock de conexão com dados opcionais"""
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
    
    if data_rows:
        for row in data_rows:
            cur.execute("INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)", row)
    
    real_conn.commit()
    
    # Wrap em MagicMock mas usar a real connection por baixo
    mock = MagicMock(wraps=real_conn)
    mock._real_conn = real_conn
    
    # Simular cache SQLite
    if not hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    repository.get_connection._sqlite_cache[id(mock)] = mock
    
    return mock


@pytest.fixture
def mock_conn():
    return create_mock_conn_with_data()


def test_list_clients_empty():
    mock = create_mock_conn_with_data()
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.list_clients()
        assert result == []


def test_list_clients_with_data():
    mock = create_mock_conn_with_data([
        ("João", 123456, 1, 100.0, 500.0),
        ("Maria", 654321, 0, None, None)
    ])
    
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.list_clients()
        assert len(result) == 2
        assert result[0]["nome"] == "João"
        assert result[1]["nome"] == "Maria"


def test_get_client_found():
    mock = create_mock_conn_with_data([("Ana", 999888, 1, 200.0, 1000.0)])
    
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.get_client(1)
        assert result is not None
        assert result["nome"] == "Ana"
        assert result["telefone"] == 999888


def test_get_client_not_found():
    mock = create_mock_conn_with_data()
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.get_client(999)
        assert result is None


def test_create_client():
    mock = create_mock_conn_with_data()
    with patch("storage.repository.get_connection", return_value=mock):
        new_client = repository.create_client({
            "nome": "Pedro",
            "telefone": 111222,
            "correntista": True,
            "score_credito": 150.0,
            "saldo_cc": 750.0
        })
        assert new_client is not None
        assert new_client["nome"] == "Pedro"
        assert new_client["id"] == 1


def test_update_client_not_found():
    mock = create_mock_conn_with_data()
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.update_client(999, {"nome": "Teste"})
        assert result is None


def test_update_client_success():
    """Testa update direto com novo mock para cada operação"""
    # get_client primeiro
    mock1 = create_mock_conn_with_data([("Original", 111, 1, 50.0, 100.0)])
    # update depois
    mock2 = create_mock_conn_with_data([("Original", 111, 1, 50.0, 100.0)])
    # get_client novamente
    mock3 = create_mock_conn_with_data([("Atualizado", 111, 1, 50.0, 100.0)])
    
    call_count = [0]
    def get_mock_sequence(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock1
        elif call_count[0] == 2:
            return mock2
        else:
            return mock3
    
    with patch("storage.repository.get_connection", side_effect=get_mock_sequence):
        updated = repository.update_client(1, {"nome": "Atualizado"})
    
    assert updated is not None
    assert updated["nome"] == "Atualizado"


def test_delete_client_not_found():
    mock = create_mock_conn_with_data()
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.delete_client(999)
        assert result is False


def test_delete_client_success():
    mock = create_mock_conn_with_data([("ToDelete", 999, 0, None, None)])
    
    # Mockar get_client para retornar que existe
    with patch("storage.repository.get_client", return_value={"id": 1, "nome": "ToDelete", "telefone": 999, "correntista": False, "score_credito": None, "saldo_cc": None}):
        with patch("storage.repository.get_connection", return_value=mock):
            result = repository.delete_client(1)
    
    assert result is True


def test_list_clients_without_cache():
    """Testa list_clients quando conexão NÃO está no cache (should_close = True)"""
    mock = create_mock_conn_with_data([("Test", 123, 1, None, None)])
    # Remover do cache para testar o branch should_close = True
    if hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.list_clients()
        assert len(result) == 1
        # Verificar que close() foi chamado
        mock.close.assert_called_once()


def test_get_client_without_cache():
    """Testa get_client quando conexão NÃO está no cache"""
    mock = create_mock_conn_with_data([("Test", 456, 0, 50.0, 100.0)])
    if hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.get_client(1)
        assert result is not None
        mock.close.assert_called_once()


def test_create_client_without_cache():
    """Testa create_client quando conexão NÃO está no cache"""
    mock = create_mock_conn_with_data()
    if hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    
    call_count = [0]
    def get_mock_sequence(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock
        else:
            # Segunda chamada é de get_client dentro de create_client
            return create_mock_conn_with_data([("New", 789, 1, None, None)])
    
    with patch("storage.repository.get_connection", side_effect=get_mock_sequence):
        result = repository.create_client({"nome": "New", "telefone": 789, "correntista": True})
        assert result is not None
        # A primeira conexão deve ter sido fechada
        assert mock.close.call_count >= 1


def test_update_client_without_cache():
    """Testa update_client quando conexão NÃO está no cache"""
    if hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    
    mock1 = create_mock_conn_with_data([("Old", 111, 1, None, None)])
    mock2 = create_mock_conn_with_data([("Old", 111, 1, None, None)])
    mock3 = create_mock_conn_with_data([("Updated", 111, 1, None, None)])
    
    call_count = [0]
    def get_mock_sequence(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock1
        elif call_count[0] == 2:
            return mock2
        else:
            return mock3
    
    with patch("storage.repository.get_connection", side_effect=get_mock_sequence):
        result = repository.update_client(1, {"nome": "Updated"})
        assert result is not None
        # Verificar que close foi chamado
        assert mock2.close.call_count >= 1


def test_delete_client_without_cache():
    """Testa delete_client quando conexão NÃO está no cache"""
    mock = create_mock_conn_with_data([("ToDelete", 999, 0, None, None)])
    if hasattr(repository.get_connection, "_sqlite_cache"):
        repository.get_connection._sqlite_cache = {}
    
    with patch("storage.repository.get_connection", return_value=mock):
        result = repository.delete_client(1)
        assert result is True
        mock.close.assert_called_once()
