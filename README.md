# ⚽ Sports Analysis Bot V2

API REST para análise estatística de jogos de futebol com sugestões de Over/Under para gols e escanteios.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## 📌 Sobre o Projeto

O Sports Analysis Bot nasceu como um script simples de terminal e evoluiu para uma API REST profissional. A V2 aplica
conceitos de arquitetura em camadas, persistência de dados e validação automática para gerar análises de jogos de
futebol com base em médias estatísticas.

### Evolução do projeto

| Versão | Tecnologia       | Descrição                                             |
|--------|------------------|-------------------------------------------------------|
| V1     | Python puro      | Script de terminal com input manual                   |
| V2     | FastAPI + SQLite | API REST com banco de dados e documentação automática |

---

## 🚀 Funcionalidades

- Cadastro de jogos com médias estatísticas
- Geração automática de análises Over/Under
- Cálculo de grau de confiança (Alta / Média / Baixa)
- Persistência de jogos e análises em banco de dados
- Validação automática de dados de entrada
- Documentação interativa via Swagger UI

---

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas com separação total de responsabilidades:

```
app/
├── main.py              # Inicialização da aplicação
├── database.py          # Configuração do banco de dados
├── models/              # Modelos ORM (tabelas)
│   ├── match.py
│   └── analysis.py
├── schemas/             # Validação de entrada e saída (Pydantic)
│   ├── match.py
│   └── analysis.py
├── services/            # Lógica de negócio
│   └── analysis_service.py
└── routers/             # Endpoints da API
    ├── matches.py
    └── analysis.py
```

---

## 🛠️ Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** — Framework web moderno e de alta performance
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para abstração do banco de dados
- **[Pydantic](https://docs.pydantic.dev/)** — Validação de dados e schemas
- **[SQLite](https://www.sqlite.org/)** — Banco de dados relacional leve
- **[Uvicorn](https://www.uvicorn.org/)** — Servidor ASGI para rodar a aplicação

---

## ⚙️ Como executar

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/pedroprogramador-x/sports-analysis-bot.git
cd sports-analysis-bot

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install fastapi uvicorn sqlalchemy pydantic-settings python-dotenv

# Configure as variáveis de ambiente
cp .env.example .env
```

### Rodando a aplicação

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: **http://127.0.0.1:8000/docs**

---

## 📡 Endpoints

### Jogos

| Método | Rota                | Descrição             |
|--------|---------------------|-----------------------|
| `POST` | `/api/matches/`     | Cadastrar novo jogo   |
| `GET`  | `/api/matches/`     | Listar todos os jogos |
| `GET`  | `/api/matches/{id}` | Buscar jogo por ID    |

### Análises

| Método | Rota                       | Descrição                  |
|--------|----------------------------|----------------------------|
| `POST` | `/api/analysis/{match_id}` | Gerar análise de um jogo   |
| `GET`  | `/api/analysis/{match_id}` | Buscar análises de um jogo |

---

## 📊 Exemplo de uso

**Cadastrar um jogo:**

```json
POST /api/matches/
{
  "team_a": "Flamengo",
  "team_b": "Vasco",
  "goals_avg_a": 1.8,
  "goals_avg_b": 1.2,
  "corners_avg_a": 6.5,
  "corners_avg_b": 5.0,
  "goals_line": 2.5,
  "corners_line": 10.5
}
```

**Resposta da análise:**

```json
{
  "goals_suggestion": "Evitar",
  "goals_confidence": "Baixa",
  "goals_diff": 0.5,
  "corners_suggestion": "Over",
  "corners_confidence": "Média",
  "corners_diff": 1.0
}
```

---

## 🔮 Próximas versões

- [ ] **V3** — PostgreSQL + Autenticação JWT + Bot do Telegram + Frontend

---

## 👨‍💻 Autor

Feito por **pedroprogramador-x**

[![GitHub](https://img.shields.io/badge/GitHub-pedroprogramador--x-black?logo=github)](https://github.com/pedroprogramador-x)