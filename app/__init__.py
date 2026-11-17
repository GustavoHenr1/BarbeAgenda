"""BarberAgenda - fábrica da aplicação Flask (padrão MVC).

  app/models       -> MODEL      (dados e regras de negócio)
  app/views        -> VIEW       (templates HTML, CSS e JavaScript)
  app/controllers  -> CONTROLLER (rotas)
"""
import os
from datetime import date, datetime

import click
from flask import Flask, render_template

from config import Config


def create_app(config_extra=None):
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    from .controllers import BLUEPRINTS
    from .controllers.auth_controller import csrf_token
    from .models import db

    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
    app.teardown_appcontext(db.close_db)
    app.jinja_env.globals["csrf_token"] = csrf_token

    _registrar_filtros(app)

    @app.errorhandler(404)
    def nao_encontrado(_e):
        return render_template("erro.html", codigo=404, mensagem="Página não encontrada."), 404

    @app.errorhandler(400)
    def requisicao_invalida(e):
        return render_template("erro.html", codigo=400, mensagem=e.description), 400

    @app.cli.command("init-db")
    def init_db_cmd():
        """Cria as tabelas (SQLite) e o usuário admin."""
        db.init_db(seed_demo=app.config["SEED_DEMO"])
        click.echo("Banco inicializado. Login: admin / senha: admin123")

    @app.cli.command("seed-admin")
    def seed_admin_cmd():
        """Cria somente o usuário admin (use após rodar schema_mysql.sql)."""
        db.init_db(seed_demo=False)
        click.echo("Usuário admin criado. Login: admin / senha: admin123")

    # Primeira execução com SQLite: cria o banco automaticamente
    if app.config["DB_ENGINE"] == "sqlite" and not os.path.exists(app.config["SQLITE_PATH"]):
        with app.app_context():
            db.init_db(seed_demo=app.config["SEED_DEMO"])

    return app


DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def _registrar_filtros(app):
    @app.template_filter("moeda")
    def moeda(valor):
        texto = f"{float(valor or 0):,.2f}"
        return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("data_br")
    def data_br(valor):
        if isinstance(valor, str):
            valor = date.fromisoformat(valor[:10])
        return valor.strftime("%d/%m/%Y")

    @app.template_filter("dia_semana")
    def dia_semana(valor):
        if isinstance(valor, str):
            valor = date.fromisoformat(valor[:10])
        return DIAS[valor.weekday()]

    @app.context_processor
    def contexto_global():
        return {"agora": datetime.now()}
