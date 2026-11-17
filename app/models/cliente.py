"""Model Cliente."""
from . import validacao as v
from .db import ErroIntegridade, consultar, executar


class Cliente:
    @staticmethod
    def listar(busca=""):
        busca = v.texto(busca)
        if busca:
            termo = f"%{busca}%"
            return consultar(
                "SELECT * FROM cliente WHERE nome LIKE ? OR telefone LIKE ? OR email LIKE ? ORDER BY nome",
                (termo, termo, termo),
            )
        return consultar("SELECT * FROM cliente ORDER BY nome")

    @staticmethod
    def buscar(id_cliente):
        return consultar("SELECT * FROM cliente WHERE id_cliente = ?", (id_cliente,), um=True)

    @staticmethod
    def contar():
        return consultar("SELECT COUNT(*) AS total FROM cliente", um=True)["total"]

    @staticmethod
    def validar(dados):
        erros = []
        v.obrigatorio(erros, dados.get("nome"), "Nome")
        v.tamanho_max(erros, dados.get("nome"), 100, "Nome")
        v.telefone(erros, dados.get("telefone"))
        v.email(erros, dados.get("email"))
        v.tamanho_max(erros, dados.get("email"), 120, "E-mail")
        return erros

    @staticmethod
    def _valores(dados):
        return (
            v.texto(dados.get("nome")),
            v.formatar_telefone(dados.get("telefone")),
            v.texto(dados.get("email")) or None,
        )

    @classmethod
    def salvar(cls, dados, id_cliente=None):
        """Cria ou atualiza. Devolve (id, lista_de_erros)."""
        erros = cls.validar(dados)
        if erros:
            return None, erros
        try:
            if id_cliente:
                executar(
                    "UPDATE cliente SET nome = ?, telefone = ?, email = ? WHERE id_cliente = ?",
                    cls._valores(dados) + (id_cliente,),
                )
                return id_cliente, []
            novo = executar("INSERT INTO cliente (nome, telefone, email) VALUES (?, ?, ?)", cls._valores(dados))
            return novo, []
        except ErroIntegridade:
            return None, ["Já existe um cliente cadastrado com este telefone."]

    @staticmethod
    def excluir(id_cliente):
        try:
            executar("DELETE FROM cliente WHERE id_cliente = ?", (id_cliente,))
            return []
        except ErroIntegridade:
            return ["Não é possível excluir: este cliente possui agendamentos registrados."]
