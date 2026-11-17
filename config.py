"""Configurações da aplicação.

Por padrão o sistema usa SQLite (arquivo local), para rodar sem instalar nada.
Para usar MySQL (ex.: na hospedagem PythonAnywhere), defina as variáveis de
ambiente DB_ENGINE=mysql, DB_HOST, DB_USER, DB_PASSWORD e DB_NAME.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

    DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite")  # "sqlite" ou "mysql"
    SQLITE_PATH = os.environ.get("SQLITE_PATH", os.path.join(BASE_DIR, "barberagenda.db"))

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "barberagenda")

    # Regras de negócio
    HORA_ABERTURA = "08:00"
    HORA_FECHAMENTO = "20:00"
    DIAS_FUNCIONAMENTO = [0, 1, 2, 3, 4, 5]  # segunda (0) a sábado (5)

    # Cria o banco e dados de exemplo automaticamente na primeira execução (SQLite)
    SEED_DEMO = os.environ.get("SEED_DEMO", "1") == "1"
