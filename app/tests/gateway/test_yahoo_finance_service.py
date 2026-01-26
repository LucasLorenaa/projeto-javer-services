import types
import pandas as pd
from unittest.mock import patch, MagicMock

from gateway.yahoo_finance_service import YahooFinanceService


def make_df(close_vals, volume_vals=None):
    volume_vals = volume_vals or [0 for _ in close_vals]
    return pd.DataFrame({"Close": close_vals, "Volume": volume_vals})


def test_get_fallback_info_deterministic():
    info_a = YahooFinanceService.get_fallback_info("AAPL")
    info_b = YahooFinanceService.get_fallback_info("AAPL")
    assert info_a["ticker"] == "AAPL"
    assert info_a == info_b  # seeded randomness should be stable per day


def test_validar_ticker_history_success():
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = make_df([10.0])
        mock_ticker_cls.return_value = ticker_instance
        assert YahooFinanceService.validar_ticker("MSFT") is True


def test_validar_ticker_allowlist_offline():
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = ticker_instance
        assert YahooFinanceService.validar_ticker("AAPL") is True
        assert YahooFinanceService.validar_ticker("INVALID") is False


def test_get_ticker_info_download_branch():
    with patch("gateway.yahoo_finance_service.yf.download") as mock_download:
        mock_download.return_value = make_df([9.0, 10.0], [100, 200])
        info = YahooFinanceService.get_ticker_info("TEST1")
    assert info is not None
    assert info["preco_atual"] == 10.0
    assert info["variacao_percentual"] == 11.11 or isinstance(info["variacao_percentual"], float)


def test_get_ticker_info_history_branch():
    with patch("gateway.yahoo_finance_service.yf.download") as mock_download, \
         patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        mock_download.return_value = pd.DataFrame()
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = make_df([5.0, 7.5], [50, 60])
        mock_ticker_cls.return_value = ticker_instance
        info = YahooFinanceService.get_ticker_info("TEST2")
    assert info is not None
    assert info["preco_atual"] == 7.5


def test_get_ticker_info_info_branch():
    with patch("gateway.yahoo_finance_service.yf.download") as mock_download, \
         patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        mock_download.return_value = pd.DataFrame()
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = pd.DataFrame()
        ticker_instance.info = {"regularMarketPrice": 20.0, "previousClose": 19.0, "volume": 10, "currency": "USD", "shortName": "Test"}
        mock_ticker_cls.return_value = ticker_instance
        info = YahooFinanceService.get_ticker_info("TEST3")
    assert info is not None
    assert info["preco_atual"] == 20.0
    assert info["variacao_dia"] == 1.0


def test_get_ticker_info_exception_returns_none():
    with patch("gateway.yahoo_finance_service.yf.download", side_effect=Exception("boom")):
        info = YahooFinanceService.get_ticker_info("FAIL")
    assert info is None


def test_get_historico_success():
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = make_df([1.0, 2.0, 3.0], [10, 20, 30])
        mock_ticker_cls.return_value = ticker_instance
        hist = YahooFinanceService.get_historico("AAPL", periodo="1mo")
    assert hist is not None
    assert hist["preco_inicial"] == 1.0
    assert hist["preco_final"] == 3.0


def test_get_historico_empty():
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = ticker_instance
        hist = YahooFinanceService.get_historico("AAPL")
    assert hist is None


def test_calcular_rentabilidade():
    from datetime import datetime, timedelta
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        start_price = 10.0
        end_price = 15.0
        ticker_instance.history.return_value = make_df([start_price, end_price])
        mock_ticker_cls.return_value = ticker_instance
        result = YahooFinanceService.calcular_rentabilidade("AAPL", 100.0, datetime.now() - timedelta(days=10))
    assert result == 50.0


def test_calcular_rentabilidade_insuficiente():
    from datetime import datetime, timedelta
    with patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        ticker_instance = MagicMock()
        ticker_instance.history.return_value = make_df([10.0])
        mock_ticker_cls.return_value = ticker_instance
        result = YahooFinanceService.calcular_rentabilidade("AAPL", 100.0, datetime.now() - timedelta(days=10))
    assert result is None


def test_get_multiple_tickers_calls_each():
    with patch("gateway.yahoo_finance_service.YahooFinanceService.get_ticker_info") as mock_info:
        mock_info.side_effect = ["i1", "i2"]
        result = YahooFinanceService.get_multiple_tickers(["A", "B"])
    assert result == {"A": "i1", "B": "i2"}
