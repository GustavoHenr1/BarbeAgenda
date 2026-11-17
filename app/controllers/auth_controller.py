"""Controller de autenticação (login / logout) e proteção das rotas."""
import functools
import secrets

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from app.models import Usuario

bp = Blueprint("auth", __name__)


def login_obrigatorio(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if g.get("usuario") is None:
            flash("Faça login para continuar.", "aviso")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


@bp.before_app_request
def carregar_usuario_e_validar_csrf():
    id_usuario = session.get("id_usuario")
    g.usuario = Usuario.buscar(id_usuario) if id_usuario else None
    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("_csrf"):
            abort(400, description="Sessão expirada. Recarregue a página e tente novamente.")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        usuario = Usuario.autenticar(request.form.get("login"), request.form.get("senha"))
        if usuario:
            token = session.get("_csrf")
            session.clear()
            session["id_usuario"] = usuario["id_usuario"]
            session["_csrf"] = token or secrets.token_hex(16)
            destino = request.args.get("next", "")
            if not destino.startswith("/") or destino.startswith("//"):
                destino = url_for("dashboard.index")
            flash(f"Bem-vindo(a), {usuario['nome']}!", "sucesso")
            return redirect(destino)
        flash("Login ou senha incorretos.", "erro")
    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("auth.login"))
