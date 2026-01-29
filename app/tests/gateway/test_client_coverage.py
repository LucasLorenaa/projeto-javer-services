"""Testes para aumentar cobertura de gateway/client.py"""
import pytest
from unittest.mock import patch
from gateway import client


def test_post_register():
    """Testa a função post_register"""
    with patch.object(client, 'get_http_client') as mock_client:
        mock_response = type('Response', (), {'status_code': 201, 'json': lambda: {'id': 1}})()
        mock_client.return_value.post.return_value = mock_response
        
        data = {
            "nome": "Test",
            "email": "test@test.com",
            "telefone": 123456,
            "senha": "Test@123",
            "data_nascimento": "2000-01-01",
            "correntista": True
        }
        
        response = client.post_register(data)
        assert response.status_code == 201
        mock_client.return_value.post.assert_called_once_with("/register", json=data)
