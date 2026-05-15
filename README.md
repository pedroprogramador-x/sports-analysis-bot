# 🏆 Sports Analysis Bot

> API REST para análise estatística de dados esportivos com predições de Machine Learning, autenticação JWT e notificações automáticas via Telegram.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black?style=flat-square&logo=jsonwebtokens)
![Status](https://img.shields.io/badge/Status-Em%20produção-brightgreen?style=flat-square)
![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)

---

## 📌 Sobre o projeto

O **Sports Analysis Bot** consome dados em tempo real da [Bzzoiro Sports Data API](https://sports.bzzoiro.com) — incluindo jogos do dia, odds de 15+ bookmakers e predições geradas por um modelo CatBoost v5.0 treinado com 163 features por jogo.

Com base nesses dados, o sistema aplica a lógica de **value betting**: só recomenda um jogo quando a probabilidade estimada pelo modelo é maior do que a probabilidade implícita precificada pelas casas. Todo dia às 9h, três picks são enviados automaticamente via Telegram para usuários cadastrados.

**Este projeto não é uma plataforma de apostas.** É um estudo aplicado de consumo de APIs, modelagem estatística, arquitetura REST e automação com Python.

---

## ⚙️ Funcionalidades

- 🔐 **Autenticação completa** — cadastro e login com JWT Bearer Token
- 📊 **Análise de value betting** — compara probabilidade do modelo vs. odds do mercado
- 📬 **Notificações automáticas via Telegram** — agendadas com APScheduler às 9h diariamente
- 🧮 **3 tipos de pick por dia:**
  - **Conservador** — odd entre 1.30 e 1.75
  - **Arrojado** — odd entre 1.75 e 3.00
  - **Acumulador** — 2 jogos combinados com odd ~4.00
- 🌐 **Documentação interativa** via Swagger UI (`/docs`)

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI |
| Banco de dados | PostgreSQL |
| ORM | SQLAlchemy |
| Autenticação | JWT (python-jose) |
| Agendador | APScheduler |
| Dados esportivos | Bzzoiro Sports Data API |
| Notificações | Telegram Bot API |
| Ambiente | Python 3.11+ / venv |
| Deploy | Railway (24h) |

---

## ☁️ Deploy em produção

O projeto está rodando **24 horas por dia** no [Railway](https://railway.app), com banco de dados PostgreSQL gerenciado pela própria plataforma.

**URL de produção:** https://web-production-f1484.up.railway.app

| Recurso | URL |
|---|---|
| API raiz | `GET /` |
| Documentação Swagger | `/docs` |
| Picks do dia | `GET /api/daily-pick/today` |

> O agendador (APScheduler) sobe automaticamente junto com a aplicação e dispara os picks às 9h via Telegram.

---

## 🚀 Como executar

### Opção A — Produção (sem instalação)

Acesse diretamente a API em produção:

```
https://web-production-f1484.up.railway.app/docs
```

### Opção B — Local

#### Pré-requisitos

- Python 3.11+
- PostgreSQL instalado e rodando
- Conta no [Telegram](https://telegram.org) e um bot criado via [@BotFather](https://t.me/botfather)

#### 1. Clone o repositório

```bash
git clone https://github.com/pedroprogramador-x/sports-analysis-bot.git
cd sports-analysis-bot
```

#### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com seus dados:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=sua_chave_secreta
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

#### 5. Inicie o servidor

```bash
uvicorn app.main:app --reload
```

Acesse a documentação em: **http://localhost:8000/docs**

---

## 📡 Endpoints principais

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/auth/register` | Cadastro de usuário | ❌ |
| POST | `/auth/login` | Login e geração de token | ❌ |
| GET | `/picks/today` | Picks do dia | ✅ |
| GET | `/picks/conservative` | Pick conservador | ✅ |
| GET | `/picks/aggressive` | Pick arrojado | ✅ |
| GET | `/picks/accumulator` | Acumulador do dia | ✅ |

> Rotas protegidas exigem header: `Authorization: Bearer <token>`

---

## 📁 Estrutura do projeto

```
Sports_analysis_bot/
├── app/
│   ├── core/           # Configurações, segurança, banco
│   ├── models/         # Modelos SQLAlchemy
│   ├── services/       # Lógica de negócio
│   │   ├── daily_pick_service.py
│   │   └── telegram_service.py
│   ├── routers/        # Endpoints FastAPI
│   └── main.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🗺️ Roadmap

- [x] Fase 1 — Consumo da BSD API e lógica de picks
- [x] Fase 2 — Autenticação JWT e sistema de usuários
- [x] Fase 3 — Notificações automáticas via Telegram + APScheduler
- [x] Fase 4 — Deploy em produção (Railway) — https://web-production-f1484.up.railway.app
- [ ] Fase 5 — Interface web (React/Next.js)

---

## 👨‍💻 Autor

**Pedro Henrique**
Estudante de Engenharia de Software | Estácio (2025–2028)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/pedrohenriquecodes)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/pedroprogramador-x)
