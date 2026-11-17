"""Camada de acesso ao banco de dados.

Funciona com SQLite (local/testes) e MySQL (produção). As consultas são
escritas com o marcador "?" e convertidas para "%s" quando o banco é MySQL.
"""
import os
import sqlite3

from flask import current_app, g


class ErroIntegridade(Exception):
    """Erro de integridade do banco (chave duplicada, chave estrangeira...)."""


def _mysql():
    return current_app.config["DB_ENGINE"] == "mysql"


def get_db():
    if "db" not in g:
        cfg = current_app.config
        if _mysql():
            import pymysql  # instalado via requirements.txt

            g.db = pymysql.connect(
                host=cfg["DB_HOST"],
                user=cfg["DB_USER"],
                password=cfg["DB_PASSWORD"],
                database=cfg["DB_NAME"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        else:
            conn = sqlite3.connect(cfg["SQLITE_PATH"])
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = conn
    return g.db


def close_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _sql(consulta):
    return consulta.replace("?", "%s") if _mysql() else consulta


def _erros_integridade():
    erros = [sqlite3.IntegrityError]
    try:
        import pymysql

        erros.append(pymysql.err.IntegrityError)
    except ImportError:
        pass
    return tuple(erros)


def consultar(sql, params=(), um=False):
    """Executa um SELECT e devolve lista de dicionários (ou um só)."""
    cur = get_db().cursor()
    cur.execute(_sql(sql), params)
    linhas = [dict(l) for l in cur.fetchall()]
    cur.close()
    if um:
        return linhas[0] if linhas else None
    return linhas


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE com commit. Devolve o id gerado."""
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(_sql(sql), params)
        db.commit()
        return cur.lastrowid
    except _erros_integridade() as e:
        db.rollback()
        raise ErroIntegridade(str(e)) from e
    finally:
        cur.close()


def init_db(seed_demo=False):
    """Cria as tabelas (somente SQLite) e o usuário administrador."""
    from werkzeug.security import generate_password_hash

    if not _mysql():
        caminho = os.path.join(os.path.dirname(__file__), "..", "..", "database", "schema_sqlite.sql")
        with open(caminho, encoding="utf-8") as f:
            get_db().executescript(f.read())

    if not consultar("SELECT id_usuario FROM usuario WHERE login = ?", ("admin",), um=True):
        executar(
            "INSERT INTO usuario (nome, login, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin", generate_password_hash("admin123"), "ADMIN"),
        )

    if seed_demo and not consultar("SELECT id_servico FROM servico", ()):
        _dados_exemplo()


def migrar():
    """Atualiza bancos criados pela versão 1.0 (adiciona colunas novas).

    Bancos novos já são criados completos pelo script schema_*.sql.
    """
    if _mysql():
        existe = consultar(
            "SELECT COUNT(*) AS n FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'profissional' AND COLUMN_NAME = 'email'",
            um=True,
        )
        if existe and not existe["n"]:
            executar("ALTER TABLE profissional ADD COLUMN email VARCHAR(120) NULL AFTER telefone")
        return
    colunas = [c["name"] for c in consultar("PRAGMA table_info(profissional)")]
    if colunas and "email" not in colunas:
        executar("ALTER TABLE profissional ADD COLUMN email TEXT")


def _dados_exemplo():
    servicos = [
        ("Corte masculino", "Corte na tesoura ou máquina", 40.00, 30),
        ("Barba", "Barba com toalha quente", 30.00, 30),
        ("Corte + Barba", "Combo corte e barba", 65.00, 60),
        ("Sobrancelha", "Acabamento na navalha", 15.00, 15),
    ]
    for s in servicos:
        executar("INSERT INTO servico (nome, descricao, preco, duracao_min) VALUES (?, ?, ?, ?)", s)
    for p in [
        ("Carlos Silva", "(11) 98888-1111", "carlos@barberagenda.com", "Cortes clássicos"),
        ("Rafael Souza", "(11) 97777-2222", "rafael@barberagenda.com", "Barba e degradê"),
    ]:
        executar("INSERT INTO profissional (nome, telefone, email, especialidade) VALUES (?, ?, ?, ?)", p)
    for c in [
        ("João Pereira", "(11) 91234-5678", "joao@email.com"),
        ("Marcos Lima", "(11) 92345-6789", "marcos@email.com"),
        ("Pedro Alves", "(11) 93456-7890", "pedro@email.com"),
    ]:
        executar("INSERT INTO cliente (nome, telefone, email) VALUES (?, ?, ?)", c)
