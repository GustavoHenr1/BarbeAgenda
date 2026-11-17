# BarberAgenda — Sistema de Agendamento para Barbearia

Projeto Integrador Transdisciplinar em Sistemas de Informação II (PIT II).

Sistema web para uma barbearia organizar **clientes, barbeiros (profissionais), serviços e
agendamentos**, impedindo que dois atendimentos do mesmo barbeiro fiquem no mesmo horário.

| Item | Escolha |
|---|---|
| Linguagem | Python 3 (back-end) + HTML, CSS e JavaScript (front-end) |
| Framework | Flask |
| Padrão de projeto | MVC (Model – View – Controller) |
| Banco de dados | MySQL 8 (produção) · SQLite (uso local e testes) |
| Testes | pytest (33 testes automatizados) |
| Hospedagem sugerida | PythonAnywhere (plano gratuito, já inclui MySQL) |

---

## 1. Estrutura do projeto (MVC)

```
barberagenda/
├── app/
│   ├── models/          ← MODEL: acesso ao banco e regras de negócio
│   │   ├── db.py            conexão (SQLite ou MySQL)
│   │   ├── cliente.py       Cliente
│   │   ├── profissional.py  Profissional
│   │   ├── servico.py       Servico
│   │   ├── agendamento.py   Agendamento (conflito de horário, expediente…)
│   │   ├── usuario.py       Usuario (login)
│   │   └── validacao.py     validações reutilizáveis
│   ├── controllers/     ← CONTROLLER: rotas (recebem a requisição e chamam o model)
│   └── views/           ← VIEW: telas
│       ├── templates/       HTML (Jinja2)
│       └── static/          CSS e JavaScript
├── database/
│   ├── schema_mysql.sql     PROJETO FÍSICO (MySQL)
│   └── schema_sqlite.sql    mesmo modelo em SQLite
├── tests/               ← testes automatizados (pytest)
├── config.py            configurações e regras (horário de funcionamento)
├── run.py               ponto de entrada
└── requirements.txt
```

## 2. Como rodar no seu computador

Pré-requisito: [Python 3.10+](https://www.python.org/downloads/) instalado.

```bash
# 1. Entre na pasta do projeto
cd barberagenda

# 2. (opcional, recomendado) crie um ambiente virtual
python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o sistema
python run.py
```

Abra **http://127.0.0.1:5000** no navegador.
Na primeira execução o banco SQLite (`barberagenda.db`) é criado sozinho, com dados de exemplo.

**Login inicial:** `admin` · **Senha:** `admin123`

### Rodar os testes automatizados

```bash
python -m pytest -v
```

## 3. Usar com MySQL

1. No MySQL, execute o arquivo `database/schema_mysql.sql` (cria o banco, as tabelas, a view e os dados iniciais).
2. Defina as variáveis de ambiente e crie o usuário admin:

```bash
# Linux/Mac (no Windows use "set" no lugar de "export")
export DB_ENGINE=mysql
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=sua_senha
export DB_NAME=barberagenda
flask --app run seed-admin
python run.py
```

## 4. Publicar na internet (PythonAnywhere — gratuito)

1. Crie uma conta em https://www.pythonanywhere.com (plano *Beginner*, gratuito).
2. Suba o código: na aba **Consoles → Bash**, rode
   `git clone https://github.com/SEU_USUARIO/barberagenda.git`
3. Instale as dependências: `pip3 install --user -r barberagenda/requirements.txt`
4. Aba **Databases**: defina uma senha do MySQL e crie o banco `barberagenda`.
   O nome real fica como `SEU_USUARIO$barberagenda`.
5. Abra um console MySQL (link na aba Databases) e cole o conteúdo de `schema_mysql.sql`
   **removendo as duas primeiras instruções** (`CREATE DATABASE` e `USE`), pois o banco já foi criado.
6. Aba **Web → Add a new web app → Manual configuration → Python 3.x**.
   - *Source code*: `/home/SEU_USUARIO/barberagenda`
   - Edite o arquivo **WSGI configuration file** e deixe assim:

```python
import os, sys
path = '/home/SEU_USUARIO/barberagenda'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DB_ENGINE'] = 'mysql'
os.environ['DB_HOST'] = 'SEU_USUARIO.mysql.pythonanywhere-services.com'
os.environ['DB_USER'] = 'SEU_USUARIO'
os.environ['DB_PASSWORD'] = 'SUA_SENHA_DO_MYSQL'
os.environ['DB_NAME'] = 'SEU_USUARIO$barberagenda'
os.environ['SECRET_KEY'] = 'coloque-uma-frase-longa-e-secreta'
from run import app as application
```

7. No console Bash, crie o admin:
   ```bash
   cd barberagenda
   DB_ENGINE=mysql DB_HOST=SEU_USUARIO.mysql.pythonanywhere-services.com DB_USER=SEU_USUARIO \
   DB_PASSWORD='SUA_SENHA' DB_NAME='SEU_USUARIO$barberagenda' python3 -m flask --app run seed-admin
   ```
8. Clique em **Reload** na aba Web. O sistema fica em `https://SEU_USUARIO.pythonanywhere.com`.

> Dica: se preferir não usar MySQL na hospedagem, pule os passos 4, 5 e 7 e remova as linhas
> `os.environ['DB_…']` do WSGI. O sistema usará SQLite automaticamente.

---

## 5. Manual de uso

### Entrar no sistema
Acesse o endereço do sistema e informe login e senha. Toda página exige login.

### Início (painel)
Mostra o resumo do dia: quantidade de atendimentos, quantos foram concluídos, o faturamento
previsto e o total de clientes, além da agenda de hoje com botões de ação rápida.

### Agenda
- Use as setas **← →** ou o calendário para trocar o dia; o botão **Hoje** volta para a data atual.
- Filtre por **profissional** e por **status**.
- Em cada agendamento:
  - **Concluir**: marca o atendimento como realizado (entra no faturamento);
  - **Editar**: muda cliente, serviço, profissional, data ou horário;
  - **Cancelar**: cancela e libera o horário (o registro continua no histórico);
  - **Reabrir**: volta um agendamento concluído/cancelado para "Agendado".

### Novo agendamento
1. Escolha o cliente (ou clique em *+ cadastrar novo cliente*), o serviço e o profissional.
2. Escolha a data. O sistema mostra os **horários livres** daquele profissional; clique em um
   deles para preencher o horário.
3. Clique em **Salvar agendamento**.

O sistema **não deixa salvar** quando:
- o profissional já tem atendimento que se sobrepõe ao horário;
- a data/hora já passou;
- é domingo (a barbearia abre de segunda a sábado);
- o serviço começa antes das 08:00 ou termina depois das 20:00;
- o profissional está inativo.

### Clientes
Cadastre nome, telefone (obrigatório e único) e e-mail. Use a busca por nome, telefone ou e-mail.
Clique no nome para ver o **histórico de atendimentos**. Um cliente com agendamentos não pode ser
excluído (para preservar o histórico).

### Profissionais
Cadastre os barbeiros. Desmarque **Ativo** para que um profissional deixe de receber novos
agendamentos sem perder o histórico.

### Serviços
Cadastre nome, descrição, preço (aceita vírgula, ex.: `40,00`) e duração em minutos. A duração é
usada para calcular o término do atendimento e verificar conflitos.

---

## 6. Regras de negócio implementadas

| Código | Regra |
|---|---|
| RN01 | Um profissional não pode ter dois atendimentos que se sobreponham no tempo. |
| RN02 | Não é permitido agendar em data/hora passada. |
| RN03 | Funcionamento de segunda a sábado, das 08:00 às 20:00 (configurável em `config.py`). |
| RN04 | O atendimento precisa terminar dentro do expediente (início + duração do serviço). |
| RN05 | Agendamento cancelado libera o horário; ao reabrir, o sistema verifica se ainda está livre. |
| RN06 | Cliente, profissional ou serviço com agendamentos não podem ser excluídos. |
| RN07 | Telefone do cliente é único; nome do serviço é único. |
| RN08 | Profissional inativo não recebe novos agendamentos. |
| RN09 | Somente agendamentos com status AGENDADO podem ser editados. |

## 7. Segurança
- Senhas guardadas com *hash* (werkzeug / PBKDF2), nunca em texto puro.
- Todas as páginas exigem login.
- Proteção contra CSRF em todos os formulários.
- Consultas SQL parametrizadas (proteção contra *SQL Injection*).
- Bloqueio de redirecionamento para sites externos após o login.
