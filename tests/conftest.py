import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402

TOKEN = "token-de-teste"


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "SQLITE_PATH": str(tmp_path / "teste.db"), "SEED_DEMO": True})


@pytest.fixture
def client(app):
    c = app.test_client()
    with c.session_transaction() as s:
        s["_csrf"] = TOKEN
    return c


@pytest.fixture
def logado(client):
    r = client.post("/login", data={"login": "admin", "senha": "admin123", "csrf_token": TOKEN})
    assert r.status_code == 302
    return client


def post(client, url, **dados):
    dados["csrf_token"] = TOKEN
    return client.post(url, data=dados, follow_redirects=True)


def proxima_segunda():
    """Uma segunda-feira no futuro (dia de funcionamento)."""
    d = date.today() + timedelta(days=7)
    return d + timedelta(days=(0 - d.weekday()) % 7)
