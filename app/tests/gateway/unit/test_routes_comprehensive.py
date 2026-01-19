"""Comprehensive unit tests for gateway CRUD routes"""
import pytest
from fastapi.testclient import TestClient
from datetime import date
from unittest.mock import Mock, patch
from gateway.main import app

client = TestClient(app)


class TestRegisterEndpoint:
    """Test /register endpoint"""
    
    def test_register_invalid_payload_missing_fields(self):
        """Test registration with missing fields"""
        payload = {"nome": "Test"}
        response = client.post("/register", json=payload)
        assert response.status_code == 422

    def test_register_invalid_email_format(self):
        """Test registration with invalid email"""
        payload = {
            "nome": "Test",
            "email": "not-an-email",
            "telefone": 21999999999,
            "data_nascimento": "1990-01-01",
            "senha": "Pass@1234"
        }
        response = client.post("/register", json=payload)
        assert response.status_code == 422

    def test_register_password_too_short(self):
        """Test registration with short password"""
        payload = {
            "nome": "Test",
            "email": "test@test.com",
            "telefone": 21999999999,
            "data_nascimento": "1990-01-01",
            "senha": "short"
        }
        response = client.post("/register", json=payload)
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test /login endpoint"""
    
    def test_login_missing_credentials(self):
        """Test login without credentials"""
        response = client.post("/login", json={})
        assert response.status_code == 422


class TestClientOut:
    """Test ClientOut model"""
    
    def test_client_out_structure(self):
        """Test ClientOut has required fields"""
        from gateway.models import ClientOut
        c = ClientOut(
            id=1,
            nome="Test",
            telefone=21999999999,
            email="test@test.com",
            data_nascimento=date(1990, 1, 1),
            correntista=False
        )
        assert c.id == 1
        assert c.nome == "Test"
