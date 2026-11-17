"""Controller de agendamentos."""
from datetime import date, timedelta

from flask import Blueprint, abort, flash, g, jsonify, redirect, render_template, request, url_for

from app.models import Agendamento, Cliente, Profissional, Servico
from .auth_controller import login_obrigatorio

bp = Blueprint("agendamentos", __name__, url_prefix="/agendamentos")


def _dia_param():
    try:
        return date.fromisoformat(request.args.get("data", ""))
    except ValueError:
        return date.today()


@bp.route("/")
@login_obrigatorio
def listar():
    dia = _dia_param()
    id_prof = request.args.get("profissional", type=int)
    status = request.args.get("status") or None
    return render_template(
        "agendamentos/lista.html",
        dia=dia,
        dia_anterior=dia - timedelta(days=1),
        dia_seguinte=dia + timedelta(days=1),
        agenda=Agendamento.listar(dia=dia.isoformat(), id_profissional=id_prof, status=status),
        resumo=Agendamento.resumo_dia(dia.isoformat()),
        profissionais=Profissional.listar(),
        filtro_prof=id_prof,
        filtro_status=status,
    )


def _opcoes(id_profissional_atual=None):
    profissionais = Profissional.listar(somente_ativos=True)
    if id_profissional_atual and not any(p["id_profissional"] == id_profissional_atual for p in profissionais):
        atual = Profissional.buscar(id_profissional_atual)
        if atual:
            profissionais.append(atual)
    return dict(clientes=Cliente.listar(), profissionais=profissionais, servicos=Servico.listar())


@bp.route("/novo", methods=["GET", "POST"])
@bp.route("/<int:id_agendamento>/editar", methods=["GET", "POST"])
@login_obrigatorio
def formulario(id_agendamento=None):
    ag = Agendamento.buscar(id_agendamento) if id_agendamento else None
    if id_agendamento and not ag:
        abort(404)
    if ag and ag["status"] != "AGENDADO":
        flash("Só é possível editar agendamentos com status AGENDADO.", "aviso")
        return redirect(url_for("agendamentos.listar", data=ag["data"]))

    dados = ag or {
        "data": request.args.get("data", date.today().isoformat()),
        "id_cliente": request.args.get("cliente", type=int),
    }
    if request.method == "POST":
        _, erros = Agendamento.salvar(request.form, g.usuario["id_usuario"], id_agendamento)
        if not erros:
            flash("Agendamento salvo com sucesso.", "sucesso")
            return redirect(url_for("agendamentos.listar", data=request.form.get("data")))
        for e in erros:
            flash(e, "erro")
        dados = {k: request.form.get(k) for k in request.form}
        for campo in ("id_cliente", "id_profissional", "id_servico"):
            dados[campo] = int(dados[campo]) if (dados.get(campo) or "").isdigit() else None

    return render_template(
        "agendamentos/form.html",
        ag=dados,
        id_agendamento=id_agendamento,
        **_opcoes(ag["id_profissional"] if ag else None),
    )


@bp.route("/<int:id_agendamento>/status", methods=["POST"])
@login_obrigatorio
def alterar_status(id_agendamento):
    ag = Agendamento.buscar(id_agendamento) or abort(404)
    erros = Agendamento.alterar_status(id_agendamento, request.form.get("status"))
    for e in erros:
        flash(e, "erro")
    if not erros:
        flash("Status atualizado.", "sucesso")
    return redirect(request.form.get("voltar") or url_for("agendamentos.listar", data=ag["data"]))


@bp.route("/<int:id_agendamento>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_agendamento):
    ag = Agendamento.buscar(id_agendamento) or abort(404)
    Agendamento.excluir(id_agendamento)
    flash("Agendamento excluído.", "sucesso")
    return redirect(url_for("agendamentos.listar", data=ag["data"]))


@bp.route("/horarios-livres")
@login_obrigatorio
def horarios_livres():
    """API usada pelo JavaScript do formulário para sugerir horários."""
    return jsonify(
        Agendamento.horarios_livres(
            request.args.get("profissional", type=int),
            request.args.get("servico", type=int),
            request.args.get("data", ""),
        )
    )
