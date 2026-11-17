"""Model Usuario (login no sistema)."""
from werkzeug.security import check_password_hash

from .db import consultar


class Usuario:
    @staticmethod
    def autenticar(login, senha):
        """Devolve o usuário se login e senha conferem, senão None."""
        u = consultar("SELECT * FROM usuario WHERE login = ?", ((login or "").strip(),), um=True)
        if u and check_password_hash(u["senha_hash"], senha or ""):
            return u
        return None

    @staticmethod
    def buscar(id_usuario):
        return consultar(
            "SELECT id_usuario, nome, login, perfil FROM usuario WHERE id_usuario = ?", (id_usuario,), um=True
        )
