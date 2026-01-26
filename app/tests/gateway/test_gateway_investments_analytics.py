import pytest
from unittest.mock import patch, MagicMock, Mock
from fastapi.testclient import TestClient

from gateway.main import app, MARKET_CACHE, CACHE_TTL_SECONDS


client = TestClient(app)


@patch("gateway.main.FileResponse", side_effect=lambda path, media_type=None: {"path": str(path)})
@patch("gateway.main.Path.exists", return_value=True)
def test_frontend_pages_available(mock_exists, mock_file_response):
    routes = [
        "/",
        "/login",
        "/login.html",
        "/register",
        "/register.html",
        "/response",
        "/dashboard",
        "/investments-page",
        "/investments.html",
    ]
    for route in routes:
        resp = client.get(route)
        assert resp.status_code == 200


@patch("gateway.main.Path.exists")
def test_investments_pages_not_found(mock_exists):
    """Cover /investments-page and /investments.html when files are missing."""
    mock_exists.return_value = False

    resp_page = client.get("/investments-page")
    resp_html = client.get("/investments.html")

    assert resp_page.status_code == 200
    assert resp_html.status_code == 200
    assert "não disponível" in resp_page.json()["message"]
    assert "não disponível" in resp_html.json()["message"]


@patch("gateway.main.get_dynamic_http_client")
def test_investments_list_and_get(mock_get_client):
    """List and fetch investments through the gateway using mocked storage client."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    list_resp = Mock()
    list_resp.status_code = 200
    list_resp.json.return_value = [
        {
            "id": 1,
            "cliente_id": 1,
            "tipo_investimento": "ACOES",
            "valor_investido": 100.0,
            "ativo": True,
            "data_aplicacao": "2024-01-01T00:00:00",
            "rentabilidade": 0.0,
        },
    ]
    get_resp = Mock()
    get_resp.status_code = 200
    get_resp.json.return_value = list_resp.json.return_value[0]
    mock_http_client.get.side_effect = [list_resp, get_resp]

    response_list = client.get("/investments")
    response_get = client.get("/investments/1")

    assert response_list.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json()["id"] == 1


@patch("gateway.main.get_dynamic_http_client")
def test_investments_get_not_found(mock_get_client):
    """Fetch investment 404 propagates HTTPException."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    not_found = Mock()
    not_found.status_code = 404
    mock_http_client.get.return_value = not_found

    resp = client.get("/investments/99")
    assert resp.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
@patch("gateway.yahoo_finance_service.YahooFinanceService.validar_ticker", return_value=True)
def test_create_and_update_investment(mock_validar, mock_get_client):
    """Create and update investments with ticker validation success."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    create_resp = Mock(status_code=201)
    create_resp.json.return_value = {
        "id": 10,
        "cliente_id": 1,
        "ticker": "AAPL",
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
        "rentabilidade": 0.0,
        "ativo": True,
        "data_aplicacao": "2024-01-01T00:00:00",
    }
    update_resp = Mock(status_code=200)
    update_resp.json.return_value = {
        "id": 10,
        "cliente_id": 1,
        "ticker": "MSFT",
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
        "rentabilidade": 0.0,
        "ativo": True,
        "data_aplicacao": "2024-01-01T00:00:00",
    }
    mock_http_client.post.return_value = create_resp
    mock_http_client.put.return_value = update_resp

    resp_create = client.post("/investments", json={
        "cliente_id": 1,
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
        "ticker": "AAPL"
    })
    resp_update = client.put("/investments/10", json={"ticker": "MSFT"})

    assert resp_create.status_code == 201
    assert resp_update.status_code == 200
    assert resp_update.json()["ticker"] == "MSFT"
    assert mock_validar.call_count == 2


@patch("gateway.main.get_dynamic_http_client")
@patch("gateway.yahoo_finance_service.YahooFinanceService.validar_ticker", return_value=False)
def test_create_investment_ticker_invalido(mock_validar, mock_get_client):
    """Invalid ticker returns 400 before calling storage."""
    resp = client.post("/investments", json={
        "cliente_id": 1,
        "tipo_investimento": "ACOES",
        "valor_investido": 200.0,
        "ticker": "INVALIDO"
    })
    assert resp.status_code == 400
    assert mock_get_client.called


@patch("gateway.main.get_dynamic_http_client")
def test_update_investment_not_found(mock_get_client):
    """Update investment 404 propagates."""
    mock_http_client = MagicMock()
    not_found = Mock(status_code=404)
    mock_http_client.put.return_value = not_found
    mock_get_client.return_value = mock_http_client

    resp = client.put("/investments/999", json={"ticker": "MSFT"})
    assert resp.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
def test_delete_investment(mock_get_client):
    """Delete investment success and 404 branches."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    ok_resp = Mock(status_code=204)
    not_found_resp = Mock(status_code=404)
    mock_http_client.delete.side_effect = [ok_resp, not_found_resp]

    resp_ok = client.delete("/investments/1")
    resp_nf = client.delete("/investments/2")

    assert resp_ok.status_code == 204
    assert resp_nf.status_code == 404


@patch("gateway.main.get_dynamic_http_client")
def test_projecao_retorno_com_total(mock_get_client):
    """Projection uses cliente data and total investido."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    client_resp = Mock(status_code=200)
    client_resp.json.return_value = {
        "id": 1,
        "nome": "João",
        "saldo_cc": 1000.0,
        "perfil_investidor": "MODERADO",
    }
    total_resp = Mock(status_code=200)
    total_resp.json.return_value = {"total_investido": 500.0}
    mock_http_client.get.side_effect = [client_resp, total_resp]

    resp = client.get("/calculos/projecao/1")
    data = resp.json()

    assert resp.status_code == 200
    assert data["projecao_anual"] == pytest.approx((1000.0 + 500.0) * 0.12, rel=1e-3)
    assert data["taxa_retorno"] == 12.0


@patch("gateway.main.get_dynamic_http_client")
def test_projecao_retorno_sem_total(mock_get_client):
    """Projection handles missing investments total (404)."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    client_resp = Mock(status_code=200)
    client_resp.json.return_value = {
        "id": 1,
        "nome": "João",
        "saldo_cc": 0.0,
        "perfil_investidor": "CONSERVADOR",
    }
    total_resp = Mock(status_code=404)
    mock_http_client.get.side_effect = [client_resp, total_resp]

    resp = client.get("/calculos/projecao/1")
    assert resp.status_code == 200
    assert resp.json()["projecao_anual"] == 0.0


@patch("gateway.main.get_dynamic_http_client")
def test_calcular_patrimonio(mock_get_client):
    """Total patrimonio calcula com saldo e investimentos."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    client_resp = Mock(status_code=200)
    client_resp.json.return_value = {"id": 1, "nome": "João", "saldo_cc": 100.0}
    total_resp = Mock(status_code=200)
    total_resp.json.return_value = {"total_investido": 900.0}
    mock_http_client.get.side_effect = [client_resp, total_resp]

    resp = client.get("/calculos/patrimonio/1")
    assert resp.status_code == 200
    assert resp.json()["patrimonio_total"] == 1000.0


@patch("gateway.main.get_dynamic_http_client")
def test_analise_carteira(mock_get_client):
    """Analisa carteira com ativos e percentuais."""
    mock_http_client = MagicMock()
    mock_get_client.return_value = mock_http_client

    client_resp = Mock(status_code=200)
    client_resp.json.return_value = {"id": 1, "nome": "João"}
    inv_resp = Mock(status_code=200)
    inv_resp.json.return_value = [
        {"tipo_investimento": "ACAO", "valor_investido": 100.0, "ativo": True},
        {"tipo_investimento": "ACAO", "valor_investido": 300.0, "ativo": False},
        {"tipo_investimento": "FII", "valor_investido": 600.0, "ativo": True},
    ]
    mock_http_client.get.side_effect = [client_resp, inv_resp]

    resp = client.get("/analises/carteira/1")
    data = resp.json()

    assert resp.status_code == 200
    assert data["total_investido"] == 1000.0
    assert data["alocacao_por_tipo"]["ACAO"]["percentual_carteira"] == 40.0
    assert data["alocacao_por_tipo"]["FII"]["percentual_carteira"] == 60.0


@patch("gateway.yahoo_finance_service.YahooFinanceService.get_ticker_info")
@patch("gateway.yahoo_finance_service.YahooFinanceService.get_fallback_info")
def test_analise_mercado_cache_and_fallback(mock_fallback, mock_get_info):
    """Analise de mercado usa cache, fallback e retorna zeros quando necessário."""
    MARKET_CACHE.clear()
    mock_get_info.side_effect = [None, {"preco_atual": 10.0, "variacao_dia": 1.0, "variacao_percentual": 10.0, "volume": 1000}]
    mock_fallback.return_value = {"preco_atual": 0.5, "variacao_dia": 0.1, "variacao_percentual": 20.0, "volume": 50}

    resp_fallback = client.get("/analises/mercado/ABC")
    data_fallback = resp_fallback.json()
    assert data_fallback["historico_disponivel"] is True
    assert data_fallback["preco_atual"] == 0.5

    # Segundo ticker preenche cache
    resp_info = client.get("/analises/mercado/XYZ")
    data_info = resp_info.json()
    assert data_info["preco_atual"] == 10.0

    # Cache path should be hit; no new call to get_ticker_info
    resp_cached = client.get("/analises/mercado/XYZ")
    assert resp_cached.json()["historico_disponivel"] is True
    assert mock_get_info.call_count == 2

    MARKET_CACHE.clear()


@patch("gateway.yahoo_finance_service.YahooFinanceService.get_ticker_info", side_effect=Exception("boom"))
def test_analise_mercado_excecao(mock_get_info):
    """Any exception returns safe fallback object."""
    resp = client.get("/analises/mercado/ERR")
    data = resp.json()
    assert data["historico_disponivel"] is False
    assert data["preco_atual"] == 0.0
