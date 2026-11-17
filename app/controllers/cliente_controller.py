"""Controller de clientes (CRUD)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Agendamento, Cliente
from .auth_controller import login_obrigatorio

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
@login_obrigatorio
def listar():
    busca = request.args.get("busca", "")
    return render_template("clientes/lista.html", clientes=Cliente.listar(busca), busca=busca)


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:id_cliente>/editar", methods=["GET", "POST"])
@login_obrigatorio
def formulario(id_cliente=None):
    cliente = Cliente.buscar(id_cliente) if id_cliente else {}
    if id_cliente and not cliente:
        abort(404)
    if request.method == "POST":
        _, erros = Cliente.salvar(request.form, id_cliente)
        if not erros:
            flash("Cliente salvo com sucesso.", "sucesso")
            return redirect(url_for("clientes.listar"))
        for e in erros:
            flash(e, "erro")
        cliente = request.form
    return render_template("clientes/form.html", cliente=cliente, id_cliente=id_cliente)


@bp.route("/<int:id_cliente>")
@login_obrigatorio
def detalhe(id_cliente):
    cliente = Cliente.buscar(id_cliente) or abort(404)
    historico = [a for a in Agendamento.listar() if a["id_cliente"] == id_cliente]
    historico.sort(key=lambda a: a["inicio"], reverse=True)
    return render_template("clientes/detalhe.html", cliente=cliente, historico=historico)


@bp.route("/<int:id_cliente>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_cliente):
    erros = Cliente.excluir(id_cliente)
    for e in erros:
        flash(e, "erro")
    if not erros:
        flash("Cliente excluído.", "sucesso")
    return redirect(url_for("clientes.listar"))
