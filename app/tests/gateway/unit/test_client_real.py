import importlib

import httpx


def test_get_http_client_real():
    import gateway.client as gwc
    importlib.reload(gwc)
    c = gwc.get_http_client()
    assert c is not None
    assert isinstance(c, httpx.Client)
    c.close()
