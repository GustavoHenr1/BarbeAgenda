from conftest import TOKEN


def test_pagina_protegida_redireciona_para_login(client):
    r = client.get("/clientes/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_login_com_senha_errada(client):
    r = client.post("/login", data={"login": "admin", "senha": "errada", "csrf_token": TOKEN})
    assert r.status_code == 200
    assert "Login ou senha incorretos" in r.get_data(as_text=True)


def test_login_correto_abre_painel(client):
    r = client.post("/login", data={"login": "admin", "senha": "admin123", "csrf_token": TOKEN}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Agenda de hoje" in html


def test_post_sem_token_csrf_e_bloqueado(client):
    r = client.post("/login", data={"login": "admin", "senha": "admin123"})
    assert r.status_code == 400


def test_logout(logado):
    r = logado.post("/logout", data={"csrf_token": TOKEN}, follow_redirects=True)
    assert "Você saiu do sistema" in r.get_data(as_text=True)
    assert logado.get("/").status_code == 302


def test_redirecionamento_externo_e_ignorado(client):
    r = client.post("/login?next=//site-malicioso.com", data={"login": "admin", "senha": "admin123", "csrf_token": TOKEN})
    assert r.headers["Location"] == "/"
