"""Controller do painel inicial."""
from datetime import date

from flask import Blueprint, render_template

from app.models import Agendamento, Cliente
from .auth_controller import login_obrigatorio

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_obrigatorio
def index():
    hoje = date.today().isoformat()
    agenda = Agendamento.listar(dia=hoje)
    return render_template(
        "dashboard.html",
        hoje=hoje,
        agenda=agenda,
        resumo=Agendamento.resumo_dia(hoje),
        total_clientes=Cliente.contar(),
    )
