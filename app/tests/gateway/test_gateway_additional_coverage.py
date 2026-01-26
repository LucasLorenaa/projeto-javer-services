import datetime
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from gateway import client as client_module
from gateway.main import app
from gateway.models import ClientCreate, ClientRegister, ClientUpdate

client = TestClient(app)


def test_get_http_client_calls_httpx():
    with patch("gateway.client.httpx.Client") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance
        result = client_module.get_http_client()
        assert result is instance
        mock_cls.assert_called_once()


@patch("gateway.main.get_dynamic_http_client")
def test_calcular_patrimonio_cliente_inexistente(mock_get_client):
    mock_http = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_http.get.return_value = mock_resp
    mock_get_client.return_value = mock_http

    resp = client.get("/calculos/patrimonio/999")
    assert resp.status_code == 404


@patch("gateway.yahoo_finance_service.YahooFinanceService.get_ticker_info", return_value=None)
@patch("gateway.yahoo_finance_service.YahooFinanceService.get_fallback_info", return_value=None)
def test_analise_mercado_sem_dados(mock_fallback, mock_info):
    resp = client.get("/analises/mercado/NODATA")
    data = resp.json()
    assert resp.status_code == 200
    assert data["historico_disponivel"] is False
    assert data["preco_atual"] == 0.0


def test_gateway_models_underage_validators():
    minor_birth = datetime.date.today().replace(year=datetime.date.today().year - 10)
    with pytest.raises(Exception):
        ClientCreate(
            nome="Menor",
            telefone=123,
            email="minor@test.com",
            data_nascimento=minor_birth,
            correntista=True,
            senha="segura123",
        )
    with pytest.raises(Exception):
        ClientRegister(
            email="minor2@test.com",
            senha="segura123",
            nome="Menor",
            telefone=123,
            data_nascimento=minor_birth,
        )
    with pytest.raises(Exception):
        ClientUpdate(data_nascimento=minor_birth)
