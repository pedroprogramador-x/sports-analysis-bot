# ⚽ Sports Analysis Bot

API de análise esportiva com pick diário automático, acumulador inteligente e notificações no Telegram — construída com FastAPI, PostgreSQL e dados reais de futebol.

---

## 🚀 Versões

| Versão | Branch | Destaques |
|--------|--------|-----------|
| V1 | `master` | Script Python com input manual, lógica Over/Under básica |
| V2 | `master` | API REST com FastAPI + SQLite, Swagger UI |
| V3 | `v3-postgres-telegram-jwt` | PostgreSQL + autenticação JWT + Telegram Bot |
| V4 | `v4-real-data-daily-pick` | BSD API (dados reais) + pick diário automático + acumulador |

---

## ✨ Funcionalidades

### Pick Diário Automático
- Busca todos os jogos do dia via BSD API (dados reais)
- Filtra entradas com **85%+ de probabilidade** e **odd ~2.00**
- Envia automaticamente no Telegram todo dia às **9h**
- Se não houver entrada boa, notifica "fique em paz" — sem entradas forçadas

### Acumulador Inteligente
- Combina 2 jogos com **75%+ de probabilidade** cada
- Odd total alvo: **~4.00**
- Exibe probabilidade combinada real de cada acumulador

### Análise Manual
- Criação de jogos e análise via API REST
- Histórico salvo no PostgreSQL
- Reenvio de análises ao Telegram via endpoint `/notify`

### Autenticação JWT
- Registro e login de usuários
- Token Bearer para rotas protegidas

---

## 🛠 Stack tecnológica

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI + Uvicorn |
| Banco de dados | PostgreSQL |
| Autenticação | JWT (python-jose + bcrypt) |
| Dados esportivos | BSD API (Bzzoiro Sports Data) |
| Agendamento | APScheduler |
| Notificações | Telegram Bot API |
| HTTP Client | httpx |
| ORM | SQLAlchemy |
| Validação | Pydantic v2 |

---

## 📂 Estrutura do projeto

```
app/
├── core/
│   └── security.py          # JWT: geração e validação de tokens
├── models/
│   ├── match.py             # Tabela de jogos
│   ├── analysis.py          # Tabela de análises
│   └── user.py              # Tabela de usuários
├── schemas/
│   ├── match.py             # Schemas de entrada/saída
│   ├── analysis.py
│   └── user.py
├── routers/
│   ├── auth.py              # /auth — registro e login
│   ├── matches.py           # /matches — CRUD de jogos
│   ├── analysis.py          # /analysis — análises manuais
│   └── daily_pick.py        # /daily-pick — pick e acumulador do dia
├── services/
│   ├── analysis_service.py  # Lógica Over/Under manual
│   ├── bsd_service.py       # Integração BSD API
│   ├── daily_pick_service.py# Seleção do pick e acumulador
│   ├── scheduler_service.py # Agendador diário (9h)
│   └── telegram_service.py  # Notificações Telegram
├── database.py              # Configuração PostgreSQL + Settings
└── main.py                  # Inicialização FastAPI + routers
```

---

## ⚙️ Variáveis de ambiente

Cria um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/sports_analysis
SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TELEGRAM_TOKEN=token_do_seu_bot
TELEGRAM_CHAT_ID=seu_chat_id
BSD_API_KEY=sua_chave_bsd
```

---

## ▶️ Como executar

```bash
# 1. Cria e ativa o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Instala as dependências
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic-settings
pip install python-jose[cryptography] passlib[bcrypt] httpx APScheduler

# 3. Configura o .env com suas variáveis

# 4. Sobe o servidor
uvicorn app.main:app --reload
```

Acessa a documentação interativa em: `http://127.0.0.1:8000/docs`

---

## 📡 Endpoints principais

### 🔐 Auth
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Registrar usuário |
| POST | `/api/auth/login` | Login + retorna JWT |

### ⚽ Matches
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/matches/` | Criar jogo manualmente |
| GET | `/api/matches/` | Listar jogos |

### 📊 Analysis
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/analysis/{match_id}` | Gerar análise + notifica Telegram |
| GET | `/api/analysis/{match_id}` | Buscar análises do jogo |
| POST | `/api/analysis/{match_id}/notify` | Reenviar análise ao Telegram |

### 🎯 Daily Pick
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/daily-pick/today` | Buscar pick do dia |
| POST | `/api/daily-pick/today/notify` | Enviar pick ao Telegram |
| POST | `/api/daily-pick/today/notify-acca` | Enviar acumulador ao Telegram |
| POST | `/api/daily-pick/today/notify-all` | Enviar pick + acumulador |

---

## 📱 Exemplo de notificação no Telegram

**Pick simples:**
```
🎯 PICK DO DIA
────────────────────────────
⚽ Manchester City vs Arsenal
🏆 Premier League
🕐 Horário: 2026-05-02T16:00:00

📌 Mercado: Over 2.5 gols
💰 Odd: 1.95
📊 Probabilidade: 87.3%

🟢 Confiança: Alta
```

**Acumulador:**
```
🎲 ACUMULADOR DO DIA — Odd ~4.12
────────────────────────────

1️⃣ Real Madrid vs Barcelona
🏆 La Liga
📌 Ambas marcam (BTTS) @ 1.95
📊 Prob: 78.4%

2️⃣ Bayern München vs Dortmund
🏆 Bundesliga
📌 Over 2.5 gols @ 2.11
📊 Prob: 76.1%

────────────────────────────
💰 Odd total: 4.12
🟡 Prob. combinada: 59.7%
```

---

## 🗺 Roadmap

- [x] V1 — Script terminal com lógica manual
- [x] V2 — API REST + Swagger
- [x] V3 — PostgreSQL + JWT + Telegram
- [x] V4 — Dados reais (BSD API) + pick diário automático + acumulador
- [ ] V4 Fase 2 — Cache Redis + histórico de acertos
- [ ] V4 Fase 3 — Dashboard web com Chart.js
- [ ] V4 Fase 4 — Deploy em produção (Railway)

---

## 👨‍💻 Autor

**Pedro** — [@pedroprogramador-x](https://github.com/pedroprogramador-x)

Projeto desenvolvido para portfólio com foco em arquitetura profissional, boas práticas e evolução incremental por versões.
