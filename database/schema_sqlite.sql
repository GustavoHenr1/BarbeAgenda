-- Versão SQLite do mesmo modelo (usada para rodar o sistema localmente
-- sem precisar instalar o MySQL, e nos testes automatizados).
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    login        TEXT NOT NULL UNIQUE,
    senha_hash   TEXT NOT NULL,
    perfil       TEXT NOT NULL DEFAULT 'ATENDENTE' CHECK (perfil IN ('ADMIN','ATENDENTE')),
    criado_em    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL,
    telefone       TEXT NOT NULL UNIQUE,
    email          TEXT,
    data_cadastro  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS profissional (
    id_profissional  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome             TEXT NOT NULL,
    telefone         TEXT,
    especialidade    TEXT,
    ativo            INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0,1))
);

CREATE TABLE IF NOT EXISTS servico (
    id_servico   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL UNIQUE,
    descricao    TEXT,
    preco        NUMERIC NOT NULL CHECK (preco >= 0),
    duracao_min  INTEGER NOT NULL CHECK (duracao_min BETWEEN 5 AND 480)
);

CREATE TABLE IF NOT EXISTS agendamento (
    id_agendamento   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente       INTEGER NOT NULL REFERENCES cliente(id_cliente) ON DELETE RESTRICT,
    id_profissional  INTEGER NOT NULL REFERENCES profissional(id_profissional) ON DELETE RESTRICT,
    id_servico       INTEGER NOT NULL REFERENCES servico(id_servico) ON DELETE RESTRICT,
    id_usuario       INTEGER NOT NULL REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    data_hora        TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'AGENDADO' CHECK (status IN ('AGENDADO','CONCLUIDO','CANCELADO')),
    observacao       TEXT,
    criado_em        TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_agendamento_prof_data ON agendamento (id_profissional, data_hora);
CREATE INDEX IF NOT EXISTS idx_agendamento_data ON agendamento (data_hora);
