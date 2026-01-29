"""Testes para aumentar cobertura dos modelos (validators)"""
import pytest
from datetime import date
from storage.models import ClientCreate, ClientUpdate, ClientRegister, InvestimentoCreate, TipoInvestimento
from gateway.models import ClientCreate as GatewayClientCreate, ClientUpdate as GatewayClientUpdate, ClientRegister as GatewayClientRegister


def test_storage_client_create_invalid_date():
    """Testa validação de data inválida no ClientCreate de storage"""
    with pytest.raises(ValueError):
        ClientCreate(
            nome="Test",
            telefone=123456,
            email="test@test.com",
            data_nascimento="invalid-date",
            correntista=True,
            score_credito=100,
            saldo_cc=500
        )


def test_storage_client_update_invalid_date():
    """Testa validação de data inválida no ClientUpdate de storage"""
    with pytest.raises(ValueError):
        ClientUpdate(data_nascimento="not-a-date")


def test_storage_client_register_invalid_date():
    """Testa validação de data inválida no ClientRegister de storage"""
    with pytest.raises(ValueError):
        ClientRegister(
            nome="Test",
            telefone=123456,
            email="test@test.com",
            data_nascimento="2024-99-99",
            senha="Test@123",
            correntista=True
        )


def test_gateway_client_create_invalid_date():
    """Testa validação de data inválida no ClientCreate de gateway"""
    with pytest.raises(ValueError):
        GatewayClientCreate(
            nome="Test",
            telefone=123456,
            email="test@test.com",
            data_nascimento="invalid",
            correntista=True,
            score_credito=100,
            saldo_cc=500
        )


def test_gateway_client_update_invalid_date():
    """Testa validação de data inválida no ClientUpdate de gateway"""
    with pytest.raises(ValueError):
        GatewayClientUpdate(data_nascimento="not-a-date")


def test_gateway_client_register_invalid_date():
    """Testa validação de data inválida no ClientRegister de gateway"""
    with pytest.raises(ValueError):
        GatewayClientRegister(
            nome="Test",
            telefone=123456,
            email="test@test.com",
            data_nascimento="abc",
            senha="Test@123",
            correntista=True
        )
