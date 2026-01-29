from unittest.mock import patch

from fastapi.testclient import TestClient

from storage.main import app


client = TestClient(app)


def make_inv(id=1):
    return {
        "id": id,
        "cliente_id": 1,
        "tipo_investimento": "ACOES",
        "ticker": "AAPL",
        "valor_investido": 100.0,
        "rentabilidade": 0.0,
        "ativo": True,
        "data_aplicacao": "2024-01-01T00:00:00",
    }


@patch("storage.main.InvestmentRepository.get_all", return_value=[make_inv()])
def test_api_list_investments(mock_repo):
    resp = client.get("/investments")
    assert resp.status_code == 200
    assert resp.json()[0]["id"] == 1


@patch("storage.main.InvestmentRepository.get_by_id", return_value=None)
def test_api_get_investment_not_found(mock_repo):
    resp = client.get("/investments/999")
    assert resp.status_code == 404


@patch("storage.main.get_client", return_value=None)
def test_api_create_investment_client_missing(mock_get_client):
    payload = {
        "cliente_id": 10,
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
    }
    resp = client.post("/investments", json=payload)
    assert resp.status_code == 404


@patch("storage.main.get_client", return_value={"id": 1, "patrimonio_investimento": 500.0})
@patch("storage.main.InvestmentRepository.create", return_value=make_inv())
def test_api_create_investment_success(mock_create, mock_get_client):
    payload = {
        "cliente_id": 1,
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
    }
    resp = client.post("/investments", json=payload)
    assert resp.status_code == 201
    assert resp.json()["id"] == 1


@patch("storage.main.get_client", return_value={"id": 1})
@patch("storage.main.InvestmentRepository.create", side_effect=ValueError("Erro"))
def test_api_create_investment_value_error(mock_create, mock_get_client):
    payload = {
        "cliente_id": 1,
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
    }
    resp = client.post("/investments", json=payload)
    assert resp.status_code == 400


@patch("storage.main.InvestmentRepository.update", return_value=None)
def test_api_update_investment_not_found(mock_update):
    resp = client.put("/investments/999", json={"valor_investido": 10})
    assert resp.status_code == 404


@patch("storage.main.InvestmentRepository.update", return_value=make_inv(id=2))
def test_api_update_investment_success(mock_update):
    resp = client.put("/investments/2", json={"valor_investido": 10})
    assert resp.status_code == 200
    assert resp.json()["id"] == 2


@patch("storage.main.InvestmentRepository.delete", return_value=False)
def test_api_delete_investment_not_found(mock_delete):
    resp = client.delete("/investments/5")
    assert resp.status_code == 404


@patch("storage.main.get_client", return_value=None)
def test_api_get_total_investido_cliente_not_found(mock_get_client):
    resp = client.get("/investments/cliente/1/total")
    assert resp.status_code == 404


@patch("storage.main.get_client", return_value={"id": 1})
@patch("storage.main.InvestmentRepository.get_total_investido_cliente", return_value=500.0)
def test_api_get_total_investido_cliente_success(mock_total, mock_get_client):
    resp = client.get("/investments/cliente/1/total")
    assert resp.status_code == 200
    assert resp.json()["total_investido"] == 500.0
