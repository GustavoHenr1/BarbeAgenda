"""Banco criado pela versão 1.0 (sem e-mail do profissional) deve ser atualizado sozinho."""
import sqlite3

from app import create_app

SCHEMA_V10 = """
CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, login TEXT NOT NULL UNIQUE,
  senha_hash TEXT NOT NULL, perfil TEXT NOT NULL DEFAULT 'ATENDENTE', criado_em TEXT);
CREATE TABLE cliente (id_cliente INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, telefone TEXT NOT NULL UNIQUE,
  email TEXT, data_cadastro TEXT);
CREATE TABLE profissional (id_profissional INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, telefone TEXT,
  especialidade TEXT, ativo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE servico (id_servico INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT,
  preco NUMERIC NOT NULL, duracao_min INTEGER NOT NULL);
CREATE TABLE agendamento (id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT, id_cliente INTEGER NOT NULL,
  id_profissional INTEGER NOT NULL, id_servico INTEGER NOT NULL, id_usuario INTEGER NOT NULL, data_hora TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'AGENDADO', observacao TEXT, criado_em TEXT);
INSERT INTO profissional (nome, telefone, especialidade) VALUES ('Antigo', NULL, 'Corte');
"""


def test_migra_banco_da_versao_1_0(tmp_path):
    caminho = tmp_path / "v10.db"
    con = sqlite3.connect(caminho)
    con.executescript(SCHEMA_V10)
    con.close()

    create_app({"TESTING": True, "SQLITE_PATH": str(caminho)})

    con = sqlite3.connect(caminho)
    colunas = [c[1] for c in con.execute("PRAGMA table_info(profissional)")]
    nome = con.execute("SELECT nome FROM profissional").fetchone()[0]
    con.close()
    assert "email" in colunas
    assert nome == "Antigo"  # dados antigos preservados
