"""Serviço para integração com Yahoo Finance API."""
from typing import Optional, Dict, Any
import yfinance as yf
from datetime import datetime, timedelta


class YahooFinanceService:
    """Serviço para consumir dados do Yahoo Finance."""

    @staticmethod
    def _fallback_seeded_random(ticker: str):
        """Gera números pseudo-determinísticos por dia para manter valores estáveis."""
        import random
        from datetime import date

        seed = f"{ticker}-{date.today().isoformat()}"
        rnd = random.Random(seed)
        return rnd

    @staticmethod
    def get_fallback_info(ticker: str) -> Optional[Dict[str, Any]]:
        """Retorna um retrato diário estável como contingência quando o Yahoo estiver indisponível."""
        base_map = {
            "^BVSP": 128000.0,
            "^GSPC": 5200.0,
            "^DJI": 39200.0,
            "^IXIC": 17800.0,
            "BTC-USD": 47000.0,
            "ETH-USD": 2400.0,
            "AAPL": 190.0,
            "MSFT": 380.0,
            "PETR4.SA": 38.0,
        }

        rnd = YahooFinanceService._fallback_seeded_random(ticker)
        base_price = base_map.get(ticker, 100.0 + rnd.uniform(-10, 10))
        drift = rnd.uniform(-0.02, 0.02)  # variação diária simulada de +/-2%
        preco_atual = round(base_price * (1 + drift), 2)
        variacao_percentual = round(drift * 100, 2)
        variacao_dia = round(preco_atual * (variacao_percentual / 100), 2)
        volume = int(abs(rnd.gauss(1_000_000, 200_000)))

        return {
            "ticker": ticker,
            "preco_atual": preco_atual,
            "preco_anterior": round(base_price, 2),
            "variacao_dia": variacao_dia,
            "variacao_percentual": variacao_percentual,
            "volume": volume,
            "moeda": "USD",
            "nome": ticker,
            "fallback": True,
        }

    @staticmethod
    def get_ticker_info(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações atuais de um ticker com abordagem resiliente:
        - Primeiro tenta via yf.download (funciona melhor para índices como ^BVSP)
        - Depois tenta via Ticker.history
        - Por último, usa Ticker.info quando disponível
        """
        try:
            # 1) Tentar via download (melhor para índices e criptos)
            try:
                dl = yf.download(ticker, period="2d", progress=False)
                if not dl.empty:
                    # Pegar último preço e anterior para variação
                    preco_atual = float(dl['Close'].iloc[-1])
                    preco_anterior = float(dl['Close'].iloc[-2]) if len(dl['Close']) > 1 else preco_atual
                    variacao_dia = preco_atual - preco_anterior
                    variacao_percentual = (variacao_dia / preco_anterior * 100) if preco_anterior else 0.0
                    volume = int(dl['Volume'].iloc[-1]) if 'Volume' in dl.columns else 0
                    return {
                        "ticker": ticker,
                        "preco_atual": round(preco_atual, 2),
                        "preco_anterior": round(preco_anterior, 2),
                        "variacao_dia": round(variacao_dia, 2),
                        "variacao_percentual": round(variacao_percentual, 2),
                        "volume": volume,
                        "moeda": "USD",
                        "nome": ticker
                    }
            except Exception:
                pass

            stock = yf.Ticker(ticker)

            # 2) Tentar histórico com Ticker.history
            hist = stock.history(period="2d")
            if not hist.empty:
                preco_atual = float(hist['Close'].iloc[-1])
                preco_anterior = float(hist['Close'].iloc[-2]) if len(hist['Close']) > 1 else preco_atual
                variacao_dia = preco_atual - preco_anterior
                variacao_percentual = (variacao_dia / preco_anterior * 100) if preco_anterior else 0.0
                volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
                return {
                    "ticker": ticker,
                    "preco_atual": round(preco_atual, 2),
                    "preco_anterior": round(preco_anterior, 2),
                    "variacao_dia": round(variacao_dia, 2),
                    "variacao_percentual": round(variacao_percentual, 2),
                    "volume": volume,
                    "moeda": "USD",
                    "nome": ticker
                }

            # 3) Por fim, tentar Ticker.info (pode falhar para alguns índices)
            info = stock.info
            if info and ('regularMarketPrice' in info or 'currentPrice' in info):
                preco_atual = info.get('regularMarketPrice') or info.get('currentPrice')
                preco_anterior = info.get('previousClose') or info.get('regularMarketPreviousClose') or 0.0
                variacao_dia = (preco_atual - preco_anterior) if (preco_atual and preco_anterior) else 0.0
                variacao_percentual = (variacao_dia / preco_anterior * 100) if (preco_anterior) else 0.0
                return {
                    "ticker": ticker,
                    "preco_atual": round(preco_atual or 0.0, 2),
                    "preco_anterior": round(preco_anterior or 0.0, 2),
                    "variacao_dia": round(variacao_dia, 2),
                    "variacao_percentual": round(variacao_percentual, 2),
                    "volume": info.get('volume') or info.get('regularMarketVolume', 0),
                    "moeda": info.get('currency', 'USD'),
                    "nome": info.get('longName') or info.get('shortName', ticker)
                }

            return None
        except Exception as e:
            print(f"Erro ao obter informações do ticker {ticker}: {e}")
            return None

    @staticmethod
    def get_historico(ticker: str, periodo: str = "1mo") -> Optional[Dict[str, Any]]:
        """
        Obtém histórico de preços de um ticker.
        
        Parâmetros:
            ticker: Código do ativo
            periodo: Período do histórico (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Retorno:
            Dicionário com dados históricos ou None
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=periodo)
            
            if hist.empty:
                return None
            
            return {
                "ticker": ticker,
                "periodo": periodo,
                "dados": hist.to_dict('records'),
                "preco_inicial": float(hist['Close'].iloc[0]),
                "preco_final": float(hist['Close'].iloc[-1]),
                "variacao_periodo": round(
                    ((float(hist['Close'].iloc[-1]) - float(hist['Close'].iloc[0])) 
                     / float(hist['Close'].iloc[0])) * 100, 
                    2
                ),
                "volume_medio": int(hist['Volume'].mean()) if 'Volume' in hist.columns else 0
            }
        
        except Exception as e:
            print(f"Erro ao obter histórico do ticker {ticker}: {e}")
            return None

    @staticmethod
    def calcular_rentabilidade(ticker: str, valor_inicial: float, data_aplicacao: datetime) -> Optional[float]:
        """
        Calcula a rentabilidade de um investimento.
        
        Parâmetros:
            ticker: Código do ativo
            valor_inicial: Valor investido inicialmente
            data_aplicacao: Data da aplicação
        
        Retorno:
            Rentabilidade percentual ou None
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Obter histórico desde a data de aplicação
            hist = stock.history(start=data_aplicacao.strftime("%Y-%m-%d"))
            
            if hist.empty or len(hist) < 2:
                return None
            
            preco_inicial = float(hist['Close'].iloc[0])
            preco_atual = float(hist['Close'].iloc[-1])
            
            rentabilidade = ((preco_atual - preco_inicial) / preco_inicial) * 100
            
            return round(rentabilidade, 2)
        
        except Exception as e:
            print(f"Erro ao calcular rentabilidade do ticker {ticker}: {e}")
            return None

    @staticmethod
    def get_multiple_tickers(tickers: list[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Obtém informações de múltiplos tickers de uma vez.
        
        Parâmetros:
            tickers: Lista de códigos de ativos
        
        Retorno:
            Dicionário com o ticker como chave e as informações como valor
        """
        resultado = {}
        
        for ticker in tickers:
            resultado[ticker] = YahooFinanceService.get_ticker_info(ticker)
        
        return resultado

    @staticmethod
    def validar_ticker(ticker: str) -> bool:
        """
        Valida se um ticker existe no Yahoo Finance.
        
        Parâmetros:
            ticker: Código do ativo
        
        Retorno:
            True se o ticker é válido, False caso contrário
        """
        allowlist = {"AAPL", "MSFT", "PETR4.SA", "^BVSP", "^GSPC", "^DJI", "^IXIC", "BTC-USD", "ETH-USD"}
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                return True
        except Exception:
            pass
        # Contingência otimista para tickers conhecidos quando offline ou no limite de requisições
        return ticker.upper() in allowlist
