import os
import httpx
import os
import httpx

STORAGE_BASE_URL = os.getenv("STORAGE_BASE_URL", "http://localhost:8001")


def get_http_client():
    return httpx.Client(
        base_url=STORAGE_BASE_URL,
        timeout=5.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )
import os
