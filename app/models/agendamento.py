"""Model Agendamento: concentra as regras de negócio da agenda."""
from datetime import date, datetime, timedelta

from flask import current_app

from . import validacao as v
from .db import consultar, executar
from .profissional import Profissional
from .servico import Servico
from .cliente import Cliente

STATUS_VALIDOS = ("AGENDADO", "CONCLUIDO", "CANCELADO")

_SELECT_DETALHADO = """
SELECT a.id_agendamento, a.id_cliente, a.id_profissional, a.id_servico, a.id_usuario,
       a.data_hora, a.status, a.observacao,
       c.nome AS cliente, c.telefone AS cliente_telefone,
       p.nome AS profissional,
       s.nome AS servico, s.preco, s.duracao_min
  FROM agendamento a
  JOIN cliente c      ON c.id_cliente = a.id_cliente
  JOIN profissional p ON p.id_profissional = a.id_profissional
  JOIN servico s      ON s.id_servico = a.id_servico
"""


def agora():
    """Isolado em função para facilitar os testes automatizados."""
    return datetime.now()


def para_datetime(valor):
    if isinstance(valor, datetime):
        return valor
    return datetime.strptime(str(valor)[:16].replace("T", " "), "%Y-%m-%d %H:%M")


def _hora(texto):
    return datetime.strptime(texto, "%H:%M").time()


def _enriquecer(linha):
    inicio = para_datetime(linha["data_hora"])
    fim = inicio + timedelta(minutes=int(linha["duracao_min"]))
    linha.update(
        inicio=inicio,
        termino=fim,
        data=inicio.strftime("%Y-%m-%d"),
        hora=inicio.strftime("%H:%M"),
        hora_fim=fim.strftime("%H:%M"),
        preco=float(linha["preco"]),
    )
    return linha


class Agendamento:
    @staticmethod
    def listar(dia=None, id_profissional=None, status=None):
        sql = _SELECT_DETALHADO + " WHERE 1 = 1"
        params = []
        if dia:
            sql += " AND DATE(a.data_hora) = ?"
            params.append(str(dia))
        if id_profissional:
            sql += " AND a.id_profissional = ?"
            params.append(int(id_profissional))
        if status:
            sql += " AND a.status = ?"
            params.append(status)
        sql += " ORDER BY a.data_hora, p.nome"
        return [_enriquecer(l) for l in consultar(sql, tuple(params))]

    @staticmethod
    def buscar(id_agendamento):
        linha = consultar(_SELECT_DETALHADO + " WHERE a.id_agendamento = ?", (id_agendamento,), um=True)
        return _enriquecer(linha) if linha else None

    @classmethod
    def resumo_dia(cls, dia):
        itens = cls.listar(dia=dia)
        validos = [a for a in itens if a["status"] != "CANCELADO"]
        return {
            "total": len(validos),
            "concluidos": sum(1 for a in itens if a["status"] == "CONCLUIDO"),
            "cancelados": sum(1 for a in itens if a["status"] == "CANCELADO"),
            "faturamento_previsto": sum(a["preco"] for a in validos),
            "faturamento_realizado": sum(a["preco"] for a in itens if a["status"] == "CONCLUIDO"),
        }

    # ------------------------------------------------------------------
    # Regras de negócio
    # ------------------------------------------------------------------
    @staticmethod
    def tem_conflito(id_profissional, inicio, duracao_min, ignorar_id=None):
        """True se o profissional já tem atendimento que se sobrepõe ao horário."""
        fim = inicio + timedelta(minutes=duracao_min)
        existentes = consultar(
            "SELECT a.id_agendamento, a.data_hora, s.duracao_min FROM agendamento a "
            "JOIN servico s ON s.id_servico = a.id_servico "
            "WHERE a.id_profissional = ? AND DATE(a.data_hora) = ? AND a.status <> 'CANCELADO'",
            (id_profissional, inicio.strftime("%Y-%m-%d")),
        )
        for e in existentes:
            if ignorar_id and int(e["id_agendamento"]) == int(ignorar_id):
                continue
            e_ini = para_datetime(e["data_hora"])
            e_fim = e_ini + timedelta(minutes=int(e["duracao_min"]))
            if inicio < e_fim and e_ini < fim:
                return True
        return False

    @classmethod
    def validar(cls, dados, id_agendamento=None):
        erros = []
        cfg = current_app.config

        cliente = Cliente.buscar(dados.get("id_cliente")) if dados.get("id_cliente") else None
        profissional = Profissional.buscar(dados.get("id_profissional")) if dados.get("id_profissional") else None
        servico = Servico.buscar(dados.get("id_servico")) if dados.get("id_servico") else None
        if not cliente:
            erros.append("Selecione um cliente.")
        if not profissional:
            erros.append("Selecione um profissional.")
        elif not profissional["ativo"]:
            erros.append("Este profissional está inativo e não pode receber agendamentos.")
        if not servico:
            erros.append("Selecione um serviço.")

        try:
            inicio = datetime.strptime(f"{v.texto(dados.get('data'))} {v.texto(dados.get('hora'))}", "%Y-%m-%d %H:%M")
        except ValueError:
            erros.append("Informe uma data e um horário válidos.")
            return erros, None

        anterior = cls.buscar(id_agendamento) if id_agendamento else None
        horario_mudou = not anterior or anterior["inicio"] != inicio
        if horario_mudou and inicio < agora():
            erros.append("Não é possível agendar em uma data/hora que já passou.")
        if inicio.weekday() not in cfg["DIAS_FUNCIONAMENTO"]:
            erros.append("A barbearia não funciona neste dia (aberta de segunda a sábado).")

        if servico:
            fim = inicio + timedelta(minutes=int(servico["duracao_min"]))
            abertura, fechamento = _hora(cfg["HORA_ABERTURA"]), _hora(cfg["HORA_FECHAMENTO"])
            if inicio.time() < abertura or fim.time() > fechamento or fim.date() != inicio.date():
                erros.append(
                    f"Horário fora do expediente ({cfg['HORA_ABERTURA']} às {cfg['HORA_FECHAMENTO']}). "
                    f"O serviço termina às {fim.strftime('%H:%M')}."
                )
            elif profissional and cls.tem_conflito(
                profissional["id_profissional"], inicio, int(servico["duracao_min"]), id_agendamento
            ):
                erros.append(f"{profissional['nome']} já tem um atendimento nesse horário. Escolha outro horário.")

        v.tamanho_max(erros, dados.get("observacao"), 255, "Observação")
        return erros, inicio

    @classmethod
    def salvar(cls, dados, id_usuario, id_agendamento=None):
        erros, inicio = cls.validar(dados, id_agendamento)
        if erros:
            return None, erros
        valores = (
            int(dados["id_cliente"]),
            int(dados["id_profissional"]),
            int(dados["id_servico"]),
            inicio.strftime("%Y-%m-%d %H:%M:00"),
            v.texto(dados.get("observacao")) or None,
        )
        if id_agendamento:
            executar(
                "UPDATE agendamento SET id_cliente = ?, id_profissional = ?, id_servico = ?, data_hora = ?, "
                "observacao = ? WHERE id_agendamento = ?",
                valores + (id_agendamento,),
            )
            return id_agendamento, []
        novo = executar(
            "INSERT INTO agendamento (id_cliente, id_profissional, id_servico, data_hora, observacao, id_usuario) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            valores + (id_usuario,),
        )
        return novo, []

    @classmethod
    def alterar_status(cls, id_agendamento, novo_status):
        if novo_status not in STATUS_VALIDOS:
            return ["Status inválido."]
        ag = cls.buscar(id_agendamento)
        if not ag:
            return ["Agendamento não encontrado."]
        if ag["status"] == "CANCELADO" and novo_status == "AGENDADO":
            if cls.tem_conflito(ag["id_profissional"], ag["inicio"], int(ag["duracao_min"]), id_agendamento):
                return ["Não foi possível reativar: o horário já foi ocupado por outro agendamento."]
        executar("UPDATE agendamento SET status = ? WHERE id_agendamento = ?", (novo_status, id_agendamento))
        return []

    @staticmethod
    def excluir(id_agendamento):
        executar("DELETE FROM agendamento WHERE id_agendamento = ?", (id_agendamento,))
        return []

    @classmethod
    def horarios_livres(cls, id_profissional, id_servico, dia):
        """Sugere horários livres (de 30 em 30 min) para o profissional no dia."""
        servico = Servico.buscar(id_servico)
        if not servico:
            return []
        cfg = current_app.config
        try:
            d = date.fromisoformat(str(dia))
        except ValueError:
            return []
        if d.weekday() not in cfg["DIAS_FUNCIONAMENTO"]:
            return []
        duracao = int(servico["duracao_min"])
        atual = datetime.combine(d, _hora(cfg["HORA_ABERTURA"]))
        fechamento = datetime.combine(d, _hora(cfg["HORA_FECHAMENTO"]))
        livres = []
        while atual + timedelta(minutes=duracao) <= fechamento:
            if atual >= agora() and not cls.tem_conflito(id_profissional, atual, duracao):
                livres.append(atual.strftime("%H:%M"))
            atual += timedelta(minutes=30)
        return livres
