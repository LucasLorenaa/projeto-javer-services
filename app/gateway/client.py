import os
import httpx

STORAGE_BASE_URL = os.getenv("STORAGE_BASE_URL", "http://storage:8001")


def get_http_client():
    return httpx.Client(
        base_url=STORAGE_BASE_URL,
        timeout=5.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )


def post_login(email: str, senha: str) -> httpx.Response:
    client = get_http_client()
    return client.post("/login", json={"email": email, "senha": senha})


def post_register(data: dict) -> httpx.Response:
    client = get_http_client()
    return client.post("/register", json=data)
