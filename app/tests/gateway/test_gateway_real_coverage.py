import httpx
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, Mock, patch

from gateway.main import app
import gateway.client as client_module

client = TestClient(app)


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    return resp


def test_get_http_client_factory():
    with patch("gateway.client.httpx.Client") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance
        result = client_module.get_http_client()
        assert result is instance
        mock_cls.assert_called_once()


@patch("gateway.main.Path.exists", return_value=False)
def test_login_route_not_found(mock_exists):
    response = client.get("/login")
    assert response.status_code == 200
    assert "dispon" in response.json()["message"].lower()


@patch("gateway.main.Path.exists", return_value=False)
def test_register_route_not_found(mock_exists):
    response = client.get("/register")
    assert response.status_code == 200
    assert "dispon" in response.json()["message"].lower()


@patch("gateway.main.get_dynamic_http_client")
def test_list_investments_by_cliente_success(mock_get_client):
    mock_http = MagicMock()
    mock_http.get.return_value = _mock_response(
        200,
        [
            {
                "id": 1,
                "cliente_id": 7,
                "tipo_investimento": "RENDA_FIXA",
                "valor_investido": 100.0,
                "rentabilidade": 0.0,
                "ativo": True,
                "data_aplicacao": "2023-01-01T00:00:00",
            }
        ],
    )
    mock_get_client.return_value = mock_http

    resp = client.get("/investments/cliente/7")
    assert resp.status_code == 200
    assert resp.json()[0]["cliente_id"] == 7


@patch("gateway.main.get_dynamic_http_client")
def test_create_investment_cliente_not_found(mock_get_client):
    mock_http = MagicMock()
    mock_resp = _mock_response(404, {"detail": "Cliente nao encontrado"})
    mock_http.post.return_value = mock_resp
    mock_get_client.return_value = mock_http

    payload = {
        "cliente_id": 99,
        "tipo_investimento": "RENDA_FIXA",
        "valor_investido": 10.0,
    }
    resp = client.post("/investments", json=payload)
    assert resp.status_code == 404


@patch("gateway.yahoo_finance_service.YahooFinanceService.validar_ticker", return_value=False)
def test_update_investment_invalid_ticker(mock_validate):
    payload = {"ticker": "FAKE", "valor_investido": 10.0}
    resp = client.put("/investments/1", json=payload)
    assert resp.status_code == 400
    assert "encontrado" in resp.json()["detail"].lower()


@patch("gateway.main.get_dynamic_http_client")
def test_projecao_retorno_cliente_not_found(mock_get_client):
    mock_http = MagicMock()
    not_found = _mock_response(404)
    mock_http.get.return_value = not_found
    mock_get_client.return_value = mock_http

    resp = client.get("/calculos/projecao/5")
    assert resp.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
def test_calcular_patrimonio_total_investimentos_fallback(mock_get_client):
    mock_http = MagicMock()
    # First call: cliente encontrado
    client_resp = _mock_response(200, {"nome": "Ana", "saldo_cc": 50.0})
    # Second call: total investido 404
    total_resp = _mock_response(404)
    mock_http.get.side_effect = [client_resp, total_resp]
    mock_get_client.return_value = mock_http

    resp = client.get("/calculos/patrimonio/7")
    data = resp.json()
    assert resp.status_code == 200
    assert data["total_investimentos"] == 0.0
    assert data["patrimonio_total"] == 50.0


@patch("gateway.main.get_dynamic_http_client")
def test_analise_carteira_cliente_not_found(mock_get_client):
    mock_http = MagicMock()
    mock_http.get.return_value = _mock_response(404)
    mock_get_client.return_value = mock_http

    resp = client.get("/analises/carteira/2")
    assert resp.status_code == 404


@patch("gateway.yahoo_finance_service.YahooFinanceService.get_ticker_info", side_effect=Exception("boom"))
def test_analise_mercado_exception_fallback(mock_info):
    resp = client.get("/analises/mercado/XYZ")
    data = resp.json()
    assert resp.status_code == 200
    assert data["historico_disponivel"] is False
    assert data["preco_atual"] == 0.0
