-- =====================================================================
--  BarberAgenda - Sistema de Agendamento para Barbearia
--  PROJETO FÍSICO DO BANCO DE DADOS (MySQL 8.x)
--  Versão 1.1 (e-mail obrigatório para cliente e profissional)
--  Gerado a partir do Diagrama de Classes (classes de persistência):
--  Usuario, Cliente, Profissional, Servico e Agendamento
-- =====================================================================

CREATE DATABASE IF NOT EXISTS barberagenda
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE barberagenda;

-- ---------------------------------------------------------------------
-- Tabela USUARIO: pessoas que acessam o sistema (dono / atendente)
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario   INT           NOT NULL AUTO_INCREMENT,
    nome         VARCHAR(100)  NOT NULL,
    login        VARCHAR(50)   NOT NULL,
    senha_hash   VARCHAR(255)  NOT NULL,
    perfil       ENUM('ADMIN','ATENDENTE') NOT NULL DEFAULT 'ATENDENTE',
    criado_em    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_login UNIQUE (login)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela CLIENTE: clientes da barbearia
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    id_cliente     INT           NOT NULL AUTO_INCREMENT,
    nome           VARCHAR(100)  NOT NULL,
    telefone       VARCHAR(20)   NOT NULL,
    email          VARCHAR(120)  NOT NULL,
    data_cadastro  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_telefone UNIQUE (telefone)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela PROFISSIONAL: barbeiros que realizam os atendimentos
-- ---------------------------------------------------------------------
CREATE TABLE profissional (
    id_profissional  INT           NOT NULL AUTO_INCREMENT,
    nome             VARCHAR(100)  NOT NULL,
    telefone         VARCHAR(20)   NULL,
    email            VARCHAR(120)  NOT NULL,
    especialidade    VARCHAR(100)  NULL,
    ativo            TINYINT(1)    NOT NULL DEFAULT 1,
    CONSTRAINT pk_profissional PRIMARY KEY (id_profissional),
    CONSTRAINT ck_profissional_ativo CHECK (ativo IN (0, 1))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela SERVICO: serviços oferecidos (corte, barba, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE servico (
    id_servico   INT           NOT NULL AUTO_INCREMENT,
    nome         VARCHAR(80)   NOT NULL,
    descricao    VARCHAR(255)  NULL,
    preco        DECIMAL(8,2)  NOT NULL,
    duracao_min  INT           NOT NULL,
    CONSTRAINT pk_servico PRIMARY KEY (id_servico),
    CONSTRAINT uq_servico_nome UNIQUE (nome),
    CONSTRAINT ck_servico_preco CHECK (preco >= 0),
    CONSTRAINT ck_servico_duracao CHECK (duracao_min BETWEEN 5 AND 480)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela AGENDAMENTO: liga Cliente, Profissional, Servico e Usuario
-- ---------------------------------------------------------------------
CREATE TABLE agendamento (
    id_agendamento   INT           NOT NULL AUTO_INCREMENT,
    id_cliente       INT           NOT NULL,
    id_profissional  INT           NOT NULL,
    id_servico       INT           NOT NULL,
    id_usuario       INT           NOT NULL,
    data_hora        DATETIME      NOT NULL,
    status           ENUM('AGENDADO','CONCLUIDO','CANCELADO') NOT NULL DEFAULT 'AGENDADO',
    observacao       VARCHAR(255)  NULL,
    criado_em        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_agendamento PRIMARY KEY (id_agendamento),
    CONSTRAINT fk_agendamento_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_agendamento_profissional FOREIGN KEY (id_profissional)
        REFERENCES profissional (id_profissional) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_agendamento_servico FOREIGN KEY (id_servico)
        REFERENCES servico (id_servico) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_agendamento_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Índice para acelerar a busca da agenda de um profissional em um dia
CREATE INDEX idx_agendamento_prof_data ON agendamento (id_profissional, data_hora);
CREATE INDEX idx_agendamento_data ON agendamento (data_hora);

-- ---------------------------------------------------------------------
-- VIEW: agenda detalhada (usada para relatórios / consultas rápidas)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_agenda_detalhada AS
SELECT a.id_agendamento,
       a.data_hora,
       a.status,
       c.nome  AS cliente,
       c.telefone,
       p.nome  AS profissional,
       s.nome  AS servico,
       s.preco,
       s.duracao_min,
       DATE_ADD(a.data_hora, INTERVAL s.duracao_min MINUTE) AS termino
  FROM agendamento a
  JOIN cliente      c ON c.id_cliente      = a.id_cliente
  JOIN profissional p ON p.id_profissional = a.id_profissional
  JOIN servico      s ON s.id_servico      = a.id_servico;

-- ---------------------------------------------------------------------
-- Dados iniciais (exemplo). O usuário administrador é criado pelo
-- comando "flask --app run seed-admin", que grava a senha criptografada.
-- ---------------------------------------------------------------------
INSERT INTO servico (nome, descricao, preco, duracao_min) VALUES
    ('Corte masculino', 'Corte na tesoura ou máquina', 40.00, 30),
    ('Barba',           'Barba com toalha quente',      30.00, 30),
    ('Corte + Barba',   'Combo corte e barba',          65.00, 60),
    ('Sobrancelha',     'Acabamento na navalha',        15.00, 15);

INSERT INTO profissional (nome, telefone, email, especialidade) VALUES
    ('Carlos Silva', '(11) 98888-1111', 'carlos@barberagenda.com', 'Cortes clássicos'),
    ('Rafael Souza', '(11) 97777-2222', 'rafael@barberagenda.com', 'Barba e degradê');

-- ---------------------------------------------------------------------
-- Migração (versão 1.1): para um banco criado com a versão 1.0, rode:
--   ALTER TABLE profissional ADD COLUMN email VARCHAR(120) NULL AFTER telefone;
-- (o sistema também faz essa migração sozinho ao iniciar)
-- ---------------------------------------------------------------------
