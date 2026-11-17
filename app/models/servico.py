"""Model Servico."""
from decimal import Decimal, InvalidOperation

from . import validacao as v
from .db import ErroIntegridade, consultar, executar


def _preco(valor):
    try:
        return Decimal(v.texto(str(valor or "")).replace(",", "."))
    except InvalidOperation:
        return None


class Servico:
    @staticmethod
    def listar():
        return consultar("SELECT * FROM servico ORDER BY nome")

    @staticmethod
    def buscar(id_servico):
        return consultar("SELECT * FROM servico WHERE id_servico = ?", (id_servico,), um=True)

    @staticmethod
    def validar(dados):
        erros = []
        v.obrigatorio(erros, dados.get("nome"), "Nome")
        v.tamanho_max(erros, dados.get("nome"), 80, "Nome")
        v.tamanho_max(erros, dados.get("descricao"), 255, "Descrição")
        preco = _preco(dados.get("preco"))
        if preco is None:
            erros.append("Preço inválido. Use números, ex.: 40,00.")
        elif preco < 0:
            erros.append("O preço não pode ser negativo.")
        try:
            duracao = int(dados.get("duracao_min") or 0)
            if not 5 <= duracao <= 480:
                erros.append("A duração deve estar entre 5 e 480 minutos.")
        except ValueError:
            erros.append("Duração inválida.")
        return erros

    @classmethod
    def salvar(cls, dados, id_servico=None):
        erros = cls.validar(dados)
        if erros:
            return None, erros
        valores = (
            v.texto(dados.get("nome")),
            v.texto(dados.get("descricao")) or None,
            str(_preco(dados.get("preco")).quantize(Decimal("0.01"))),
            int(dados.get("duracao_min")),
        )
        try:
            if id_servico:
                executar(
                    "UPDATE servico SET nome = ?, descricao = ?, preco = ?, duracao_min = ? WHERE id_servico = ?",
                    valores + (id_servico,),
                )
                return id_servico, []
            return executar(
                "INSERT INTO servico (nome, descricao, preco, duracao_min) VALUES (?, ?, ?, ?)", valores
            ), []
        except ErroIntegridade:
            return None, ["Já existe um serviço com este nome."]

    @staticmethod
    def excluir(id_servico):
        try:
            executar("DELETE FROM servico WHERE id_servico = ?", (id_servico,))
            return []
        except ErroIntegridade:
            return ["Não é possível excluir: este serviço já foi usado em agendamentos."]
