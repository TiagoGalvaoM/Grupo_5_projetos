# NexoClima - Guia Rápido de Início

## 🚀 Setup Rápido (10 minutos)

### 1. Criar Contas (Gratuitas)

#### MongoDB Atlas
1. Acesse: https://www.mongodb.com/cloud/atlas/register
2. Crie cluster gratuito (M0)
3. Crie usuário do banco
4. Whitelist IP: `0.0.0.0/0` (desenvolvimento)
5. Copie connection string

#### Neon PostgreSQL
1. Acesse: https://neon.tech/
2. Crie projeto gratuito
3. Copie connection string

### 2. Configurar Projeto

```bash
cd NexoClima_Code
cp .env.example .env
```

Edite `.env` com suas credenciais:
```env
MONGODB_URI=mongodb+srv://SEU_USER:SUA_SENHA@cluster.mongodb.net/
DATABASE_URL=postgresql://SEU_USER:SUA_SENHA@ep-xxx.region.aws.neon.tech/nexoclima
```

### 3. Backend

```bash
cd backend
pip install poetry
poetry install
poetry run alembic upgrade head
poetry run python scripts/seed_initial_data.py
poetry run uvicorn app.main:app --reload
```

✅ Backend rodando em: http://localhost:8000

### 4. Executar Pipeline (Primeira Coleta)

Em outro terminal:
```bash
cd backend
poetry run python scripts/run_pipeline_manual.py
```

Você verá:
```
INFO - Fetching weather data from Open-Meteo
INFO - Weather data fetched successfully
INFO - RAW data saved to MongoDB
INFO - Transformed XXX measurements
INFO - Pipeline completed successfully
```

### 5. Frontend

Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```

✅ Dashboard rodando em: http://localhost:5173

## 🎯 Verificação de Funcionamento

### ✅ Checklist

1. **Backend API funcionando**
   - Acesse: http://localhost:8000/docs
   - Teste endpoint: `GET /health`
   - Deve retornar: `{"status": "healthy"}`

2. **Dados no MongoDB**
   - Via MongoDB Compass ou shell:
   ```javascript
   use nexoclima_raw
   db.raw_ingestions.countDocuments()
   // Deve retornar > 0
   ```

3. **Dados no PostgreSQL**
   - Via Neon dashboard ou psql:
   ```sql
   SELECT COUNT(*) FROM measurements;
   -- Deve retornar > 0
   ```

4. **Dashboard exibindo dados**
   - Acesse: http://localhost:5173
   - Deve mostrar:
     - ✅ Últimas medições (temperatura, precipitação, etc)
     - ✅ Status da fonte "open_meteo"
     - ✅ Gráfico de série temporal

5. **Scheduler automático**
   - Logs do backend devem mostrar:
   ```
   INFO - Scheduler started - Weather pipeline will run every 60 minutes
   ```

## 📊 Endpoints Principais

### Backend (http://localhost:8000)

```bash
# Health check
curl http://localhost:8000/health

# Últimas medições
curl http://localhost:8000/api/v1/measurements/latest

# Status das fontes
curl http://localhost:8000/api/v1/sources/status

# Histórico do pipeline
curl http://localhost:8000/api/v1/pipeline/runs
```

### Frontend (http://localhost:5173)

- Dashboard interativo
- Gráficos em tempo real
- Seletor de indicadores

## 🔄 Fluxo Completo de Dados

```
Open-Meteo API (dados reais)
    ↓
Backend FastAPI (ingestão)
    ↓
MongoDB Atlas (RAW - payload original)
    ↓
Transformação (normalização)
    ↓
Neon PostgreSQL (CURATED - dados estruturados)
    ↓
API REST (endpoints)
    ↓
Dashboard React (visualização)
```

## 🛠️ Comandos Úteis

### Executar pipeline manualmente
```bash
cd backend
poetry run python scripts/run_pipeline_manual.py
```

### Ver logs do backend
```bash
cd backend
poetry run uvicorn app.main:app --reload --log-level debug
```

### Recriar banco do zero
```bash
cd backend
poetry run alembic downgrade base
poetry run alembic upgrade head
poetry run python scripts/seed_initial_data.py
```

### Build do frontend
```bash
cd frontend
npm run build
```

## ❌ Problemas Comuns

### Backend não inicia
- Verifique `.env` existe
- Verifique credenciais MongoDB e Neon
- Teste connection strings separadamente

### Nenhum dado no dashboard
- Execute pipeline primeiro: `poetry run python scripts/run_pipeline_manual.py`
- Verifique backend está rodando
- Verifique console do navegador para erros

### Erro de CORS
- Backend já tem CORS configurado
- Verifique se backend está em http://localhost:8000
- Verifique proxy no `frontend/vite.config.ts`

### MongoDB "duplicate key error"
- Normal! Significa que payload já foi coletado
- Pipeline está funcionando corretamente (idempotência)

## 📖 Próximos Passos

1. Aguardar 60 minutos para scheduler executar automaticamente
2. Explorar documentação em `docs/`
3. Ver ADRs em `docs/decisions/`
4. Adicionar segunda fonte de dados (Fase 2)

## 🎓 Demonstração ao Professor

Você pode mostrar:

1. **Código consumindo API real** (Open-Meteo)
2. **MongoDB com payloads originais**
3. **PostgreSQL com dados transformados**
4. **Dashboard com dados reais**
5. **Rastreabilidade completa** (measurements → raw_ingestions)
6. **Pipeline automático** (scheduler logs)
7. **Nenhum dado mockado**

## 📚 Documentação Completa

- [README Principal](README.md)
- [Setup Detalhado](SETUP_INSTRUCTIONS.md)
- [Arquitetura](docs/architecture.md)
- [Pipeline de Dados](docs/data-pipeline.md)
- [Modelo de Dados](docs/database-model.md)
