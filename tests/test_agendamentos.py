from datetime import date, timedelta

from conftest import post, proxima_segunda


def agendar(c, hora="10:00", dia=None, cliente=1, prof=1, servico=1, **extra):
    dia = dia or proxima_segunda().isoformat()
    return post(c, "/agendamentos/novo", id_cliente=cliente, id_profissional=prof, id_servico=servico,
                data=dia, hora=hora, **extra).get_data(as_text=True)


def test_agendamento_valido(logado):
    html = agendar(logado)
    assert "Agendamento salvo com sucesso" in html
    assert "João Pereira" in html


def test_conflito_de_horario_mesmo_profissional(logado):
    agendar(logado, hora="10:00", servico=3)          # Corte + Barba = 60 min (10:00–11:00)
    html = agendar(logado, hora="10:30", cliente=2)   # sobrepõe
    assert "já tem um atendimento nesse horário" in html


def test_sem_conflito_com_outro_profissional(logado):
    agendar(logado, hora="10:00")
    html = agendar(logado, hora="10:00", cliente=2, prof=2)
    assert "Agendamento salvo com sucesso" in html


def test_horario_logo_apos_termino_e_permitido(logado):
    agendar(logado, hora="10:00")                     # 30 min → termina 10:30
    html = agendar(logado, hora="10:30", cliente=2)
    assert "Agendamento salvo com sucesso" in html


def test_data_no_passado(logado):
    html = agendar(logado, dia="2020-01-06")
    assert "já passou" in html


def test_domingo_bloqueado(logado):
    domingo = proxima_segunda() - timedelta(days=1)
    html = agendar(logado, dia=domingo.isoformat())
    assert "não funciona neste dia" in html


def test_fora_do_expediente(logado):
    assert "fora do expediente" in agendar(logado, hora="07:30")
    assert "fora do expediente" in agendar(logado, hora="19:45")  # termina 20:15


def test_campos_obrigatorios(logado):
    html = post(logado, "/agendamentos/novo", id_cliente="", id_profissional="", id_servico="",
                data="", hora="").get_data(as_text=True)
    assert "Selecione um cliente" in html
    assert "Informe uma data e um horário válidos" in html


def test_cancelar_libera_horario(logado):
    agendar(logado, hora="14:00")
    post(logado, "/agendamentos/1/status", status="CANCELADO")
    html = agendar(logado, hora="14:00", cliente=2)
    assert "Agendamento salvo com sucesso" in html


def test_reabrir_cancelado_com_horario_ocupado(logado):
    agendar(logado, hora="14:00")
    post(logado, "/agendamentos/1/status", status="CANCELADO")
    agendar(logado, hora="14:00", cliente=2)
    html = post(logado, "/agendamentos/1/status", status="AGENDADO").get_data(as_text=True)
    assert "horário já foi ocupado" in html


def test_concluir_soma_faturamento(logado):
    dia = proxima_segunda().isoformat()
    agendar(logado, hora="09:00", dia=dia)  # R$ 40
    post(logado, "/agendamentos/1/status", status="CONCLUIDO")
    html = logado.get(f"/agendamentos/?data={dia}").get_data(as_text=True)
    assert "R$ 40,00" in html
    assert "Concluído" in html


def test_editar_agendamento_mantendo_horario(logado):
    agendar(logado, hora="11:00")
    ag = proxima_segunda().isoformat()
    html = post(logado, "/agendamentos/1/editar", id_cliente=1, id_profissional=1, id_servico=1,
                data=ag, hora="11:00", observacao="Trazer foto do corte").get_data(as_text=True)
    assert "Agendamento salvo com sucesso" in html
    assert "Trazer foto do corte" in html


def test_cliente_com_agendamento_nao_pode_ser_excluido(logado):
    agendar(logado)
    html = post(logado, "/clientes/1/excluir").get_data(as_text=True)
    assert "possui agendamentos" in html


def test_profissional_inativo_nao_recebe_agendamento(logado):
    post(logado, "/profissionais/2/editar", nome="Rafael Souza", telefone="", especialidade="", email="r@b.com")
    html = agendar(logado, prof=2)
    assert "inativo" in html


def test_api_horarios_livres(logado):
    dia = proxima_segunda().isoformat()
    agendar(logado, hora="08:00", dia=dia, servico=3)  # ocupa 08:00–09:00
    livres = logado.get(f"/agendamentos/horarios-livres?profissional=1&servico=1&data={dia}").get_json()
    assert "08:00" not in livres and "08:30" not in livres
    assert "09:00" in livres
    assert livres[-1] == "19:30"


def test_historico_do_cliente(logado):
    agendar(logado)
    html = logado.get("/clientes/1").get_data(as_text=True)
    assert "Histórico de atendimentos" in html
    assert "Corte masculino" in html


# ---------------------------------------------------------------------
# Versão 1.1 — correções apontadas nos testes com os colegas
# ---------------------------------------------------------------------
def test_horario_fora_da_grade_e_recusado(logado):
    """Luiz Felipe: era possível agendar às 15:32."""
    html = agendar(logado, hora="15:32")
    assert "Horário inválido" in html
    assert "Agendamento salvo com sucesso" not in html


def test_horario_na_grade_e_aceito(logado):
    assert "Agendamento salvo com sucesso" in agendar(logado, hora="15:30")


def test_editar_sem_mudar_horario_nao_exige_grade(logado, app):
    """Agendamentos antigos fora da grade continuam editáveis (ex.: só trocar a observação)."""
    dia = proxima_segunda().isoformat()
    with app.app_context():
        from app.models.db import executar
        executar("INSERT INTO agendamento (id_cliente,id_profissional,id_servico,id_usuario,data_hora) "
                 "VALUES (1,1,1,1,?)", (f"{dia} 10:10:00",))
    html = post(logado, "/agendamentos/1/editar", id_cliente=1, id_profissional=1, id_servico=1,
                data=dia, hora="10:10", observacao="ok").get_data(as_text=True)
    assert "Agendamento salvo com sucesso" in html


def test_resumo_respeita_filtro_de_profissional(logado):
    """Luiz: com filtro de profissional, os totais mostravam o dia inteiro."""
    dia = proxima_segunda().isoformat()
    agendar(logado, hora="09:00", dia=dia, prof=1)
    agendar(logado, hora="10:00", dia=dia, prof=1, cliente=2)
    agendar(logado, hora="09:00", dia=dia, prof=2, cliente=3)
    html = logado.get(f"/agendamentos/?data={dia}&profissional=1").get_data(as_text=True)
    total = html.split("Atendimentos</span>")[1].split("</span>")[0]
    assert ">2" in total
    assert "R$ 80,00" in html


def test_filtro_por_periodo_data_ate(logado):
    """Luigi: filtrar vários dias com o campo "até"."""
    seg = proxima_segunda()
    ter = seg + timedelta(days=1)
    agendar(logado, hora="09:00", dia=seg.isoformat())
    agendar(logado, hora="11:00", dia=ter.isoformat(), cliente=2)
    html = logado.get(f"/agendamentos/?data={seg.isoformat()}&ate={ter.isoformat()}").get_data(as_text=True)
    assert "João Pereira" in html and "Marcos Lima" in html
    assert "período de 2 dias" in html
    # sem o "até", mostra só o primeiro dia
    html = logado.get(f"/agendamentos/?data={seg.isoformat()}").get_data(as_text=True)
    assert "João Pereira" in html and "Marcos Lima" not in html


def test_periodo_com_data_final_antes_da_inicial(logado):
    seg = proxima_segunda()
    html = logado.get(f"/agendamentos/?data={seg.isoformat()}&ate={(seg - timedelta(days=3)).isoformat()}",
                      follow_redirects=True).get_data(as_text=True)
    assert "não pode ser anterior" in html


def test_api_horarios_livres_ignora_o_proprio_agendamento(logado):
    dia = proxima_segunda().isoformat()
    agendar(logado, hora="08:00", dia=dia)
    livres = logado.get(f"/agendamentos/horarios-livres?profissional=1&servico=1&data={dia}&ignorar=1").get_json()
    assert "08:00" in livres
