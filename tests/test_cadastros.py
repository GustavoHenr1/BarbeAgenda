from conftest import post


def test_cadastrar_cliente(logado):
    r = post(logado, "/clientes/novo", nome="Ana Costa", telefone="11999998888", email="ana@email.com")
    html = r.get_data(as_text=True)
    assert "Cliente salvo com sucesso" in html
    assert "(11) 99999-8888" in html  # telefone formatado


def test_cliente_sem_nome_e_telefone_invalido(logado):
    html = post(logado, "/clientes/novo", nome="", telefone="123").get_data(as_text=True)
    assert "O campo Nome é obrigatório" in html
    assert "Telefone inválido" in html


def test_cliente_email_invalido(logado):
    html = post(logado, "/clientes/novo", nome="Ana", telefone="11999998888", email="ana@").get_data(as_text=True)
    assert "E-mail inválido" in html


def test_cliente_telefone_duplicado(logado):
    html = post(logado, "/clientes/novo", nome="Outro", telefone="(11) 91234-5678").get_data(as_text=True)
    assert "Já existe um cliente cadastrado com este telefone" in html


def test_buscar_cliente(logado):
    html = logado.get("/clientes/?busca=Marcos").get_data(as_text=True)
    assert "Marcos Lima" in html
    assert "João Pereira" not in html


def test_editar_e_excluir_cliente(logado):
    post(logado, "/clientes/1/editar", nome="João P. Pereira", telefone="(11) 91234-5678", email="")
    assert "João P. Pereira" in logado.get("/clientes/").get_data(as_text=True)
    html = post(logado, "/clientes/1/excluir").get_data(as_text=True)
    assert "Cliente excluído" in html


def test_servico_preco_negativo_e_duracao_invalida(logado):
    html = post(logado, "/servicos/novo", nome="Pigmentação", preco="-5", duracao_min="2").get_data(as_text=True)
    assert "O preço não pode ser negativo" in html
    assert "A duração deve estar entre 5 e 480 minutos" in html


def test_servico_aceita_preco_com_virgula(logado):
    html = post(logado, "/servicos/novo", nome="Pigmentação", preco="25,50", duracao_min="20").get_data(as_text=True)
    assert "Serviço salvo com sucesso" in html
    assert "R$ 25,50" in html


def test_servico_nome_duplicado(logado):
    html = post(logado, "/servicos/novo", nome="Barba", preco="10", duracao_min="20").get_data(as_text=True)
    assert "Já existe um serviço com este nome" in html


def test_profissional_cadastro_e_desativacao(logado):
    post(logado, "/profissionais/novo", nome="Lucas", especialidade="Navalhado", telefone="", ativo="1")
    html = post(logado, "/profissionais/3/editar", nome="Lucas", especialidade="Navalhado", telefone="").get_data(as_text=True)
    assert "Inativo" in html


def test_pagina_inexistente(logado):
    assert logado.get("/clientes/999/editar").status_code == 404
