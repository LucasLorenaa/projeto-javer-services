"""Testes para investimentos."""
import pytest
from storage.investment_repository import InvestmentRepository
from storage.models import InvestimentoCreate, TipoInvestimento
from datetime import datetime


class TestInvestmentRepository:
    """Testes para o repositório de investimentos."""

    def test_create_investment(self):
        """Testa criação de investimento."""
        investimento = InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.ACOES,
            ticker="PETR4.SA",
            valor_investido=1000.0,
            rentabilidade=5.5,
            ativo=True
        )
        
        resultado = InvestmentRepository.create(investimento)
        
        assert resultado.id is not None
        assert resultado.cliente_id == 1
        assert resultado.tipo_investimento == TipoInvestimento.ACOES
        assert resultado.ticker == "PETR4.SA"
        assert resultado.valor_investido == 1000.0
        assert resultado.rentabilidade == 5.5
        assert resultado.ativo == True

    def test_get_by_id(self):
        """Testa obtenção de investimento por ID."""
        investimento = InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.FUNDOS,
            ticker="FI123",
            valor_investido=500.0,
            ativo=True
        )
        
        criado = InvestmentRepository.create(investimento)
        obtido = InvestmentRepository.get_by_id(criado.id)
        
        assert obtido is not None
        assert obtido.id == criado.id
        assert obtido.cliente_id == 1

    def test_get_by_cliente(self):
        """Testa obtenção de investimentos por cliente."""
        # Criar alguns investimentos para o cliente 1
        for i in range(3):
            inv = InvestimentoCreate(
                cliente_id=1,
                tipo_investimento=TipoInvestimento.RENDA_FIXA,
                valor_investido=100.0 * (i + 1),
                ativo=True
            )
            InvestmentRepository.create(inv)
        
        # Criar investimentos para cliente 2
        inv = InvestimentoCreate(
            cliente_id=2,
            tipo_investimento=TipoInvestimento.CRIPTO,
            valor_investido=200.0,
            ativo=True
        )
        InvestmentRepository.create(inv)
        
        # Verificar que obtém apenas investimentos do cliente 1
        investimentos = InvestmentRepository.get_by_cliente(1)
        
        assert len(investimentos) >= 3
        assert all(inv.cliente_id == 1 for inv in investimentos)

    def test_update_investment(self):
        """Testa atualização de investimento."""
        from storage.models import InvestimentoUpdate
        
        investimento = InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.ACOES,
            valor_investido=1000.0,
            rentabilidade=0.0,
            ativo=True
        )
        
        criado = InvestmentRepository.create(investimento)
        
        # Atualizar
        atualizacao = InvestimentoUpdate(
            rentabilidade=10.5,
            ativo=False
        )
        
        atualizado = InvestmentRepository.update(criado.id, atualizacao)
        
        assert atualizado.rentabilidade == 10.5
        assert atualizado.ativo == False

    def test_delete_investment(self):
        """Testa exclusão de investimento."""
        investimento = InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.FUNDOS,
            valor_investido=500.0,
            ativo=True
        )
        
        criado = InvestmentRepository.create(investimento)
        
        # Deletar
        resultado = InvestmentRepository.delete(criado.id)
        
        assert resultado == True
        
        # Verificar se foi realmente deletado
        obtido = InvestmentRepository.get_by_id(criado.id)
        assert obtido is None

    def test_get_total_investido_cliente(self):
        """Testa cálculo do total investido por cliente."""
        # Limpar investimentos do cliente 1
        investimentos = InvestmentRepository.get_by_cliente(1)
        for inv in investimentos:
            InvestmentRepository.delete(inv.id)
        
        # Criar novos investimentos
        InvestmentRepository.create(InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.ACOES,
            valor_investido=1000.0,
            ativo=True
        ))
        
        InvestmentRepository.create(InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.FUNDOS,
            valor_investido=500.0,
            ativo=True
        ))
        
        InvestmentRepository.create(InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.RENDA_FIXA,
            valor_investido=300.0,
            ativo=False  # Inativo, não deve ser contado
        ))
        
        total = InvestmentRepository.get_total_investido_cliente(1)
        
        assert total == 1500.0  # Apenas os ativos

    def test_get_all(self):
        """Testa obtenção de todos os investimentos."""
        investimentos = InvestmentRepository.get_all()
        
        assert isinstance(investimentos, list)
        assert len(investimentos) >= 0


class TestYahooFinanceService:
    """Testes para o serviço do Yahoo Finance."""

    def test_validar_ticker_valido(self):
        """Testa validação de ticker válido."""
        from gateway.yahoo_finance_service import YahooFinanceService
        
        # AAPL é um ticker válido
        resultado = YahooFinanceService.validar_ticker("AAPL")
        
        assert resultado == True

    def test_validar_ticker_invalido(self):
        """Testa validação de ticker inválido."""
        from gateway.yahoo_finance_service import YahooFinanceService
        
        # XYZ123XYZ é um ticker inválido
        resultado = YahooFinanceService.validar_ticker("XYZ123XYZ")
        
        assert resultado == False


class TestInvestmentModels:
    """Testes para os modelos de investimento."""

    def test_investimento_create_valido(self):
        """Testa criação de modelo InvestimentoCreate válido."""
        investimento = InvestimentoCreate(
            cliente_id=1,
            tipo_investimento=TipoInvestimento.ACOES,
            ticker="PETR4.SA",
            valor_investido=1000.0,
            rentabilidade=5.0,
            ativo=True
        )
        
        assert investimento.cliente_id == 1
        assert investimento.tipo_investimento == TipoInvestimento.ACOES
        assert investimento.valor_investido == 1000.0

    def test_investimento_create_valor_negativo(self):
        """Testa que valor negativo causa erro."""
        with pytest.raises(ValueError):
            InvestimentoCreate(
                cliente_id=1,
                tipo_investimento=TipoInvestimento.ACOES,
                valor_investido=-100.0,
                ativo=True
            )

    def test_tipo_investimento_enum(self):
        """Testa enum TipoInvestimento."""
        assert TipoInvestimento.RENDA_FIXA.value == "RENDA_FIXA"
        assert TipoInvestimento.ACOES.value == "ACOES"
        assert TipoInvestimento.FUNDOS.value == "FUNDOS"
        assert TipoInvestimento.CRIPTO.value == "CRIPTO"
