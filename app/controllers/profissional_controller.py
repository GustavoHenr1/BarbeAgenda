"""Controller de profissionais (CRUD)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Profissional
from .auth_controller import login_obrigatorio

bp = Blueprint("profissionais", __name__, url_prefix="/profissionais")


@bp.route("/")
@login_obrigatorio
def listar():
    return render_template("profissionais/lista.html", profissionais=Profissional.listar())


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:id_profissional>/editar", methods=["GET", "POST"])
@login_obrigatorio
def formulario(id_profissional=None):
    prof = Profissional.buscar(id_profissional) if id_profissional else {"ativo": 1}
    if id_profissional and not prof:
        abort(404)
    if request.method == "POST":
        _, erros = Profissional.salvar(request.form, id_profissional)
        if not erros:
            flash("Profissional salvo com sucesso.", "sucesso")
            return redirect(url_for("profissionais.listar"))
        for e in erros:
            flash(e, "erro")
        prof = request.form
    return render_template("profissionais/form.html", prof=prof, id_profissional=id_profissional)


@bp.route("/<int:id_profissional>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_profissional):
    erros = Profissional.excluir(id_profissional)
    for e in erros:
        flash(e, "erro")
    if not erros:
        flash("Profissional excluído.", "sucesso")
    return redirect(url_for("profissionais.listar"))
