# ⚽ Sports Analysis Bot V3

API REST para análise estatística de jogos de futebol com sugestões de Over/Under para gols e escanteios, notificações via Telegram e autenticação JWT.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?logo=postgresql)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)
![JWT](https://img.shields.io/badge/JWT-Auth-black?logo=jsonwebtokens)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## 📌 Sobre o Projeto

O Sports Analysis Bot nasceu como um script simples de terminal e evoluiu para uma API REST profissional com autenticação, banco de dados robusto e integração com Telegram.

### Evolução do projeto

| Versão | Tecnologia | Descrição |
|--------|------------|-----------|
| V1 | Python puro | Script de terminal com input manual |
| V2 | FastAPI + SQLite | API REST com banco de dados e documentação automática |
| V3 | FastAPI + PostgreSQL + JWT + Telegram | API profissional com autenticação e notificações em tempo real |

---

## 🚀 Funcionalidades

- Cadastro de jogos com médias estatísticas
- Geração automática de análises Over/Under
- Cálculo de grau de confiança (Alta / Média / Baixa)
- Persistência de jogos e análises em PostgreSQL
- Validação automática de dados de entrada
- Autenticação com JWT (registro e login)
- Notificações automáticas via Telegram ao gerar análise
- Endpoint para reenviar análises existentes ao Telegram
- Documentação interativa via Swagger UI

---

## 🏗️ Arquitetura

```
app/
├── main.py                     # Inicialização da aplicação
├── database.py                 # Configuração do PostgreSQL
├── core/
│   └── security.py             # JWT — geração e validação de tokens
├── models/                     # Modelos ORM (tabelas)
│   ├── match.py
│   ├── analysis.py
│   └── user.py
├── schemas/                    # Validação de entrada e saída (Pydantic)
│   ├── match.py
│   ├── analysis.py
│   └── user.py
├── services/                   # Lógica de negócio
│   ├── analysis_service.py     # Cálculo Over/Under
│   └── telegram_service.py     # Envio de notificações
└── routers/                    # Endpoints da API
    ├── auth.py                 # Registro e login
    ├── matches.py
    └── analysis.py
```

---

## 🛠️ Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** — Framework web moderno e de alta performance
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para abstração do banco de dados
- **[PostgreSQL](https://www.postgresql.org/)** — Banco de dados relacional robusto
- **[Pydantic](https://docs.pydantic.dev/)** — Validação de dados e schemas
- **[Python-Jose](https://python-jose.readthedocs.io/)** — Geração e validação de tokens JWT
- **[Passlib](https://passlib.readthedocs.io/)** — Hash seguro de senhas com bcrypt
- **[HTTPX](https://www.python-httpx.org/)** — Cliente HTTP para integração com Telegram
- **[Uvicorn](https://www.uvicorn.org/)** — Servidor ASGI para rodar a aplicação

---

## ⚙️ Como executar

### Pré-requisitos

- Python 3.11+
- PostgreSQL instalado e rodando
- Bot do Telegram criado via @BotFather

### Instalação

```bash
# Clone o repositório
git clone https://github.com/pedroprogramador-x/sports-analysis-bot.git
cd sports-analysis-bot

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Instale as dependências
pip install fastapi uvicorn sqlalchemy pydantic-settings python-dotenv
pip install python-jose[cryptography] passlib[bcrypt] httpx psycopg2-binary

# Configure as variáveis de ambiente
cp .env.example .env
```

### Variáveis de ambiente (.env)

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/sports_analysis_v3
APP_NAME=Sports Analysis Bot v3
DEBUG=True
TELEGRAM_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_CHAT_ID=SEU_CHAT_ID_AQUI
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Rodando a aplicação

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: **http://127.0.0.1:8000/docs**

---

## 📡 Endpoints

### Auth

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/auth/register` | Cadastrar novo usuário |
| `POST` | `/api/auth/login` | Login e geração de token JWT |

### Jogos

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/matches/` | Cadastrar novo jogo |
| `GET` | `/api/matches/` | Listar todos os jogos |
| `GET` | `/api/matches/{id}` | Buscar jogo por ID |

### Análises

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/analysis/{match_id}` | Gerar análise e notificar Telegram |
| `GET` | `/api/analysis/{match_id}` | Buscar análises de um jogo |
| `POST` | `/api/analysis/{match_id}/notify` | Reenviar análise ao Telegram |

---

## 📊 Exemplo de uso

**1. Registrar usuário:**
```json
POST /api/auth/register
{
  "username": "pedro",
  "password": "123456"
}
```

**2. Fazer login:**
```
POST /api/auth/login
username=pedro&password=123456
```
Retorna:
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

**3. Cadastrar um jogo:**
```json
POST /api/matches/
{
  "team_a": "Flamengo",
  "team_b": "Vasco",
  "goals_avg_a": 2.1,
  "goals_avg_b": 1.3,
  "corners_avg_a": 6.5,
  "corners_avg_b": 5.0,
  "goals_line": 2.5,
  "corners_line": 10.5
}
```

**4. Gerar análise (notifica Telegram automaticamente):**
```
POST /api/analysis/1
```

**Notificação recebida no Telegram:**
```
⚽ Flamengo vs Vasco
────────────────────────────
🥅 GOLS
  📈 Sugestão: Over
  🟡 Confiança: Média
  📊 Diferença: +0.90

🚩 ESCANTEIOS
  📈 Sugestão: Over
  🟡 Confiança: Média
  📊 Diferença: +1.00
```

---

## 🔮 Próximas versões

- [ ] **V4** — Frontend web + proteção de rotas com JWT + histórico de análises

---

## 👨‍💻 Autor

Feito por **pedroprogramador-x**

[![GitHub](https://img.shields.io/badge/GitHub-pedroprogramador--x-black?logo=github)](https://github.com/pedroprogramador-x)        
