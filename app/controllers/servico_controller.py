"""Controller de serviços (CRUD)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Servico
from .auth_controller import login_obrigatorio

bp = Blueprint("servicos", __name__, url_prefix="/servicos")


@bp.route("/")
@login_obrigatorio
def listar():
    return render_template("servicos/lista.html", servicos=Servico.listar())


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:id_servico>/editar", methods=["GET", "POST"])
@login_obrigatorio
def formulario(id_servico=None):
    servico = Servico.buscar(id_servico) if id_servico else {}
    if id_servico and not servico:
        abort(404)
    if request.method == "POST":
        _, erros = Servico.salvar(request.form, id_servico)
        if not erros:
            flash("Serviço salvo com sucesso.", "sucesso")
            return redirect(url_for("servicos.listar"))
        for e in erros:
            flash(e, "erro")
        servico = request.form
    return render_template("servicos/form.html", servico=servico, id_servico=id_servico)


@bp.route("/<int:id_servico>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_servico):
    erros = Servico.excluir(id_servico)
    for e in erros:
        flash(e, "erro")
    if not erros:
        flash("Serviço excluído.", "sucesso")
    return redirect(url_for("servicos.listar"))
