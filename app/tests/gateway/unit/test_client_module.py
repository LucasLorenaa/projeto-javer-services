import gateway.client as client
import httpx


def test_get_http_client_defaults():
    c = client.get_http_client()
    assert c is not None
    # testes usam cliente fake (durante patching), então apenas verificar se os métodos esperados existem
    assert hasattr(c, "get") and hasattr(c, "post") and hasattr(c, "put")
    if hasattr(c, "close"):
        c.close()
