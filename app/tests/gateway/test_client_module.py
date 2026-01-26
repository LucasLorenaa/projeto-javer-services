import os
from unittest.mock import patch, MagicMock

from gateway import client as client_module


def test_get_http_client_uses_env(monkeypatch):
    monkeypatch.setattr(client_module, "STORAGE_BASE_URL", "http://example.com")
    http_client = client_module.get_http_client()
    assert http_client.timeout is not None


def test_post_register_calls_http_client():
    with patch("gateway.client.httpx.Client") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance
        mock_response = MagicMock()
        mock_instance.post.return_value = mock_response

        data = {"email": "test@test.com"}
        resp = client_module.post_register(data)

        mock_instance.post.assert_called_with("/register", json=data)
        assert resp is mock_response
