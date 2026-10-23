# NexoClima Backend

Backend do sistema NexoClima, responsável por:

- Consumir APIs externas de dados climáticos e saúde
- Armazenar dados brutos no MongoDB Atlas
- Transformar e padronizar dados heterogêneos
- Persistir dados tratados no Neon PostgreSQL
- Classificar situações de interesse
- Expor APIs para o dashboard
- Integração futura com LLM e MCP

## Tecnologias

- Python 3.12+
- FastAPI
- SQLAlchemy + Alembic
- MongoDB (via PyMongo)
- PostgreSQL (Neon)
- APScheduler

## Estrutura

```
app/
├── api/          # Endpoints REST
├── core/         # Configuração, logging, segurança
├── db/           # Conexões com bancos de dados
├── domain/       # Modelos de domínio
├── ingestion/    # Conectores com fontes externas
├── transformation/ # ETL e normalização
├── classification/ # Regras de classificação
├── schemas/      # Pydantic schemas
└── services/     # Lógica de negócio
```

## Instalação

```bash
cd backend
poetry install
```

## Configuração

Copie `.env.example` para `.env` e configure as variáveis:

```bash
cp ../.env.example .env
```

Variáveis obrigatórias:
- `MONGODB_URI`: Connection string do MongoDB Atlas
- `DATABASE_URL`: Connection string do Neon PostgreSQL

## Migrações

```bash
# Criar migração
poetry run alembic revision --autogenerate -m "descrição"

# Aplicar migrações
poetry run alembic upgrade head
```

## Execução

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testes

```bash
poetry run pytest
poetry run pytest --cov=app tests/
```

## Pipeline de Dados

```
API Externa → MongoDB Atlas (RAW) → Transformação → Neon (CURATED) → API → Dashboard
```

Ver documentação completa em `../docs/`
