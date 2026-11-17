"""Model Profissional (barbeiro)."""
from . import validacao as v
from .db import ErroIntegridade, consultar, executar


class Profissional:
    @staticmethod
    def listar(somente_ativos=False):
        if somente_ativos:
            return consultar("SELECT * FROM profissional WHERE ativo = 1 ORDER BY nome")
        return consultar("SELECT * FROM profissional ORDER BY ativo DESC, nome")

    @staticmethod
    def buscar(id_profissional):
        return consultar("SELECT * FROM profissional WHERE id_profissional = ?", (id_profissional,), um=True)

    @staticmethod
    def validar(dados):
        erros = []
        v.obrigatorio(erros, dados.get("nome"), "Nome")
        v.tamanho_max(erros, dados.get("nome"), 100, "Nome")
        v.telefone(erros, dados.get("telefone"), obrigatorio_=False)
        v.tamanho_max(erros, dados.get("especialidade"), 100, "Especialidade")
        return erros

    @classmethod
    def salvar(cls, dados, id_profissional=None):
        erros = cls.validar(dados)
        if erros:
            return None, erros
        valores = (
            v.texto(dados.get("nome")),
            v.formatar_telefone(dados.get("telefone")) or None,
            v.texto(dados.get("especialidade")) or None,
            1 if dados.get("ativo") else 0,
        )
        if id_profissional:
            executar(
                "UPDATE profissional SET nome = ?, telefone = ?, especialidade = ?, ativo = ? WHERE id_profissional = ?",
                valores + (id_profissional,),
            )
            return id_profissional, []
        return executar(
            "INSERT INTO profissional (nome, telefone, especialidade, ativo) VALUES (?, ?, ?, ?)", valores
        ), []

    @staticmethod
    def excluir(id_profissional):
        try:
            executar("DELETE FROM profissional WHERE id_profissional = ?", (id_profissional,))
            return []
        except ErroIntegridade:
            return ["Não é possível excluir: este profissional possui agendamentos. Desative-o em vez de excluir."]
