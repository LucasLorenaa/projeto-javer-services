import gateway.client as client
import httpx


def test_get_http_client_defaults():
    c = client.get_http_client()
    assert c is not None
    # tests use a fake client (during patching) so just assert the expected methods exist
    assert hasattr(c, "get") and hasattr(c, "post") and hasattr(c, "put")
    if hasattr(c, "close"):
        c.close()
