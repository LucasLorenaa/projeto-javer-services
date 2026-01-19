"""Testes para API endpoints do gateway - validações de requisições"""
import pytest
from datetime import date
from gateway.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_cliente_create_sem_dados():
    """Requisição sem dados obrigatórios deve falhar"""
    response = client.post("/register", json={})
    assert response.status_code == 422


def test_cliente_login_sem_dados():
    """Login sem dados obrigatórios deve falhar"""
    response = client.post("/login", json={})
    assert response.status_code == 422


def test_validacao_email_gateway():
    """Email inválido no gateway"""
    payload = {
        "nome": "Test",
        "email": "invalid-email",
        "telefone": 21987654321,
        "data_nascimento": "1990-01-01",
        "senha": "Senha@123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_validacao_idade_gateway():
    """Idade menor que 18 no gateway"""
    payload = {
        "nome": "Jovem",
        "email": "jovem@test.com",
        "telefone": 21987654321,
        "data_nascimento": "2015-01-01",  # Menor de idade
        "senha": "Senha@123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_validacao_senha_curta_gateway():
    """Senha muito curta no gateway"""
    payload = {
        "nome": "Test",
        "email": "test@test.com",
        "telefone": 21987654321,
        "data_nascimento": "1990-01-01",
        "senha": "123"  # Senha muito curta
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422
