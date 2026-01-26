import pandas as pd
from unittest.mock import MagicMock, patch

from gateway.yahoo_finance_service import YahooFinanceService


def test_get_ticker_info_returns_none_when_all_sources_empty():
    empty_df = pd.DataFrame()
    with patch("gateway.yahoo_finance_service.yf.download", return_value=empty_df), \
         patch("gateway.yahoo_finance_service.yf.Ticker") as mock_ticker_cls:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = empty_df
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        result = YahooFinanceService.get_ticker_info("ZZZ")
        assert result is None


def test_get_historico_exception_returns_none():
    with patch("gateway.yahoo_finance_service.yf.Ticker", side_effect=Exception("fail")):
        assert YahooFinanceService.get_historico("ZZZ") is None


def test_calcular_rentabilidade_exception_returns_none():
    with patch("gateway.yahoo_finance_service.yf.Ticker", side_effect=Exception("fail")):
        assert YahooFinanceService.calcular_rentabilidade("ZZZ", 100.0, pd.Timestamp("2020-01-01")) is None


def test_validar_ticker_allowlist_fallback_true():
    with patch("gateway.yahoo_finance_service.yf.Ticker", side_effect=Exception("fail")):
        assert YahooFinanceService.validar_ticker("AAPL") is True
