# Instruções de Setup - NexoClima

## Estado Atual do Projeto

✅ **BACKEND COMPLETO** - Primeira vertical slice implementada

O sistema está pronto para:
1. Consumir API Open-Meteo (dados meteorológicos reais)
2. Armazenar RAW no MongoDB Atlas
3. Transformar dados
4. Persistir no Neon PostgreSQL
5. Expor via API REST
6. Execução automática (scheduler)

## Pré-requisitos

### 1. Criar conta MongoDB Atlas (FREE)

1. Acesse: https://www.mongodb.com/cloud/atlas/register
2. Crie cluster gratuito
3. Crie um database user
4. Whitelist IP (0.0.0.0/0 para desenvolvimento)
5. Copie connection string:
   ```
   mongodb+srv://<user>:<password>@cluster.mongodb.net/
   ```

### 2. Criar conta Neon PostgreSQL (FREE)

1. Acesse: https://neon.tech/
2. Crie projeto
3. Copie connection string:
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/nexoclima
   ```

## Instalação

### 1. Configure `.env`

```bash
cd NexoClima_Code
cp .env.example .env
```

Edite `.env`:
```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://SEU_USER:SUA_SENHA@cluster.mongodb.net/
MONGODB_DATABASE=nexoclima_raw

# Neon PostgreSQL
DATABASE_URL=postgresql://SEU_USER:SUA_SENHA@ep-xxx.region.aws.neon.tech/nexoclima

# Outras configs já estão corretas
```

### 2. Instale Backend

```bash
cd backend

# Instalar Poetry
pip install poetry

# Instalar dependências
poetry install
```

### 3. Crie banco de dados

```bash
# Criar tabelas via Alembic
poetry run alembic upgrade head

# Popular dados iniciais
poetry run python scripts/seed_initial_data.py
```

Você verá:
```
INFO - Created 1 data sources
INFO - Created 7 indicators
INFO - Created 1 territories
INFO - Database seed completed successfully!
```

### 4. Teste o Pipeline Manualmente

```bash
poetry run python scripts/run_pipeline_manual.py
```

Saída esperada:
```
INFO - Starting manual pipeline execution...
INFO - MongoDB connected successfully
INFO - PostgreSQL (Neon) connected successfully
INFO - Starting ingestion for open_meteo
INFO - Fetching weather data from Open-Meteo
INFO - Weather data fetched successfully
INFO - RAW data saved to MongoDB
INFO - Starting transformation
INFO - Transformed XXX measurements
INFO - Persisting XXX measurements
INFO - Pipeline completed successfully
```

### 5. Inicie o servidor

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Saída:
```
INFO - NexoClima API started successfully
INFO - Scheduler started - Weather pipeline will run every 60 minutes
```

### 6. Teste a API

Abra navegador: http://localhost:8000/docs

Endpoints disponíveis:
- `GET /health` - Verifica conexões
- `GET /api/v1/measurements/latest` - Últimas medições
- `GET /api/v1/sources/status` - Status das fontes
- `GET /api/v1/pipeline/runs` - Histórico de execuções

### 7. Consulte dados no MongoDB

```javascript
// Via MongoDB Compass ou mongo shell
use nexoclima_raw
db.raw_ingestions.find().limit(1).pretty()
```

Você verá o payload original da API Open-Meteo.

### 8. Consulte dados no PostgreSQL

```sql
-- Via psql ou Neon Dashboard

-- Ver últimas medições
SELECT
    i.name as indicator,
    m.value,
    m.unit,
    m.reference_time
FROM measurements m
JOIN indicators i ON m.indicator_id = i.id
ORDER BY m.reference_time DESC
LIMIT 10;

-- Status das fontes
SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 5;
```

## Verificação de Funcionamento

### ✅ Pipeline RAW → CURATED funcionando se:

1. **MongoDB tem documentos em `raw_ingestions`**
   ```javascript
   db.raw_ingestions.countDocuments()
   // Deve retornar > 0
   ```

2. **PostgreSQL tem medições**
   ```sql
   SELECT COUNT(*) FROM measurements;
   -- Deve retornar > 0
   ```

3. **API retorna dados**
   ```bash
   curl http://localhost:8000/api/v1/measurements/latest
   # Deve retornar JSON com medições
   ```

4. **Scheduler executa automaticamente**
   - Aguarde 60 minutos OU
   - Rode manualmente: `poetry run python scripts/run_pipeline_manual.py`

## Próximos Passos

### Frontend (Pendente)

1. Criar projeto React com Vite
2. Configurar TypeScript
3. Consumir API do backend
4. Criar dashboard com:
   - Cards de última coleta
   - Gráfico de série temporal
   - Status das fontes

### Fase 2

1. Adicionar segunda fonte de dados
2. Implementar classificação de risco
3. Integração LLM

## Troubleshooting

### Erro: "MongoDB connection failed"
- Verifique `MONGODB_URI` no `.env`
- Confira whitelist de IPs no MongoDB Atlas
- Teste connection string via MongoDB Compass

### Erro: "PostgreSQL connection failed"
- Verifique `DATABASE_URL` no `.env`
- Confira se banco existe no Neon
- URL deve começar com `postgresql://` (não `postgres://`)

### Erro: "Source open_meteo not found in database"
- Execute: `poetry run python scripts/seed_initial_data.py`

### Erro: "Indicator X not found in database"
- Execute seed novamente
- Verifique se todos os 7 indicadores foram criados:
  ```sql
  SELECT code FROM indicators;
  ```

### Pipeline não executa automaticamente
- Verifique logs: scheduler deve mostrar "Scheduler started"
- Aguarde intervalo configurado (60 min padrão)
- Ou execute manualmente: `scripts/run_pipeline_manual.py`

## Comandos Úteis

```bash
# Ver logs em tempo real
poetry run uvicorn app.main:app --reload --log-level debug

# Executar pipeline manualmente
poetry run python scripts/run_pipeline_manual.py

# Criar nova migração
poetry run alembic revision --autogenerate -m "descrição"

# Aplicar migrações
poetry run alembic upgrade head

# Reverter migração
poetry run alembic downgrade -1

# Testes (quando implementados)
poetry run pytest
poetry run pytest --cov=app tests/
```

## Validação de Sucesso da POC

Você pode demonstrar ao professor:

1. ✅ **API real sendo consumida** (Open-Meteo)
2. ✅ **Payload bruto no MongoDB Atlas**
3. ✅ **Transformação aplicada**
4. ✅ **Dados tratados no Neon PostgreSQL**
5. ✅ **API interna funcionando** (FastAPI)
6. ✅ **Rastreabilidade** (raw_ingestion_id liga CURATED → RAW)
7. ✅ **Pipeline automático** (scheduler)
8. ✅ **Observabilidade** (pipeline_runs, logs)
9. ✅ **Idempotência** (re-executar não duplica)
10. ✅ **Nenhum dado mockado**

## Arquivos Principais

```
backend/
├── app/
│   ├── main.py                     # Aplicação FastAPI
│   ├── core/config.py              # Configurações
│   ├── db/                         # Conexões MongoDB/PostgreSQL
│   ├── domain/models.py            # Modelos SQLAlchemy
│   ├── ingestion/
│   │   ├── base.py                 # Classe base conector
│   │   └── weather_connector.py    # Conector Open-Meteo
│   ├── transformation/
│   │   └── weather_transformer.py  # Transformador Weather
│   ├── services/
│   │   ├── pipeline_service.py     # Orquestrador do pipeline
│   │   └── scheduler.py            # Agendador
│   ├── api/v1/                     # Endpoints REST
│   └── schemas/                    # Pydantic schemas
├── scripts/
│   ├── seed_initial_data.py        # Popular dados iniciais
│   └── run_pipeline_manual.py      # Executar pipeline manual
├── alembic/                        # Migrações
├── pyproject.toml                  # Dependências
└── README.md
```

## Suporte

- **Documentação**: Ver `docs/` (architecture, data-pipeline, etc)
- **ADRs**: Ver `docs/decisions/`
- **README principal**: `README.md`
