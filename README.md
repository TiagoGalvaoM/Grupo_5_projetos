# 🌡️ NexoClima Dashboard

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)
![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)

**Sistema integrado de vigilância em saúde e clima para a Secretaria de Saúde do Recife**

[Instalação](#-instalação) • [Uso](#-uso) • [Arquitetura](#-arquitetura) • [API](#-endpoints-da-api)

</div>

---

## 📋 Sobre o Projeto

O **NexoClima** é uma plataforma de monitoramento que integra dados climáticos e epidemiológicos para apoiar a **Vigilância em Saúde / Vigidesastres da Secretaria de Saúde do Recife**. O sistema coleta, processa e visualiza informações de múltiplas fontes em tempo real, permitindo análise de correlações entre clima e doenças transmitidas por vetores.

**Projeto acadêmico** da disciplina Projetos 5 — Sistemas de Informação — CESAR School.

### 🎯 Objetivos

- **Monitoramento Climático**: Dados de temperatura, precipitação, umidade e vento em tempo real
- **Vigilância Epidemiológica**: Acompanhamento de casos de dengue, zika e chikungunya
- **Rastreabilidade Total**: Pipeline completo RAW → CURATED com rastreamento de origem
- **Visualização Intuitiva**: Dashboard interativo com gráficos e indicadores de alerta
- **Dados Reais**: ❌ NENHUM DADO MOCKADO no fluxo funcional

---

## ✨ Funcionalidades

### 🌤️ Dados Climáticos
- ☁️ Integração com **Open-Meteo API**
- 🌡️ Temperatura, precipitação, umidade relativa
- 💨 Velocidade do vento e código meteorológico
- 📊 Gráficos de série temporal interativos

### 🦟 Dados Epidemiológicos
- 📈 Integração com **InfoDengue API** (SINAN/MS)
- 🏥 Casos estimados e notificados de dengue, zika e chikungunya
- 🚨 Níveis de alerta por doença (verde, amarelo, laranja, vermelho)
- 📅 Dados organizados por semana epidemiológica
- 📊 Gráficos temporais de evolução de casos

### 🔄 Pipeline de Dados
- **Ingestão Automatizada**: Coleta periódica de APIs externas
- **Armazenamento Dual**: MongoDB (RAW) + PostgreSQL (CURATED)
- **Transformação**: ETL com validação e enriquecimento
- **Deduplicação**: Hash-based para evitar duplicatas
- **Rastreabilidade**: Proveniência completa dos dados
- **Idempotência**: Pipeline pode ser reexecutado sem duplicação

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + TypeScript + Recharts + Vite                       │
│  http://localhost:5173                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                      BACKEND                                 │
│  FastAPI + Python 3.12 + SQLAlchemy + Motor                 │
│  http://localhost:8000                                       │
├──────────────────────────────────────────────────────────────┤
│                    PIPELINE SERVICE                          │
│  Ingestion → Transformation → Storage                       │
└───────────┬─────────────────────────┬────────────────────────┘
            │                         │
    ┌───────▼────────┐       ┌───────▼────────┐
    │   MongoDB      │       │   PostgreSQL   │
    │   (RAW Layer)  │       │ (CURATED Layer)│
    │  Atlas Cloud   │       │   Neon Cloud   │
    └────────────────┘       └────────────────┘
            ▲                         ▲
            │                         │
    ┌───────┴────────┐       ┌───────┴────────┐
    │  Open-Meteo    │       │   InfoDengue   │
    │  Weather API   │       │  Epidemio API  │
    └────────────────┘       └────────────────┘
```

### 📊 Fluxo de Dados

1. **Ingestão**: Conector específico busca dados da API externa
2. **RAW**: Payload original armazenado no MongoDB Atlas com hash
3. **Transformação**: ETL normaliza dados para modelo interno
4. **CURATED**: Dados estruturados persistidos no Neon PostgreSQL
5. **API**: FastAPI expõe endpoints REST
6. **Dashboard**: React consome API e exibe dados reais

### 🗄️ Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 |
| Ingestão | httpx (async) |
| RAW Storage | MongoDB Atlas (NoSQL) |
| CURATED Storage | PostgreSQL (Neon Serverless) |
| Transformação | Pydantic, custom transformers |
| ORM & Migrations | SQLAlchemy, Alembic |
| Frontend | React 18, TypeScript, Vite |
| Gráficos | Recharts |
| Deploy | Docker (opcional), Neon, Atlas |

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.12+**
- **Node.js 18+**
- **Poetry** (gerenciador de dependências Python)
- **MongoDB Atlas** (conta gratuita - free tier 512MB)
- **PostgreSQL/Neon** (conta gratuita - free tier 512MB)

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/seu-usuario/nexoclima.git
cd NexoClima_Code
```

### 2️⃣ Configuração do Backend

```bash
cd backend

# Instalar Poetry (se não tiver)
pip install poetry

# Instalar dependências
poetry install

# Criar arquivo .env
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# PostgreSQL (Neon ou local)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/nexoclima

# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DATABASE=nexoclima_raw

# Configurações
ENVIRONMENT=development
LOG_LEVEL=INFO
PIPELINE_VERSION=0.1.0
```

> ⚠️ **IMPORTANTE**: Nunca commite `.env` no git

**Executar migrações:**

```bash
poetry run alembic upgrade head
```

**Popular dados iniciais:**

```bash
# Criar fontes, indicadores climáticos e território (Recife)
poetry run python scripts/seed_initial_data.py

# Adicionar indicadores epidemiológicos (dengue, zika, chikungunya)
poetry run python scripts/add_epidemiology_data.py
```

### 3️⃣ Configuração do Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Criar arquivo .env (opcional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

---

## 🎮 Uso

### Iniciar Backend

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API disponível em: **http://localhost:8000**
- **Documentação interativa**: http://localhost:8000/docs (Swagger UI)
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

Dashboard disponível em: **http://localhost:5173**

### Executar Pipeline Manualmente

**Pipeline Climático (Open-Meteo):**
```bash
cd backend
poetry run python scripts/run_pipeline_manual.py
```

Isso irá:
1. ☁️ Consumir API Open-Meteo
2. 💾 Armazenar RAW no MongoDB Atlas
3. 🔄 Transformar dados
4. ✅ Persistir no Neon PostgreSQL

**Pipeline Epidemiológico (InfoDengue):**
```bash
poetry run python scripts/run_infodengue_pipeline.py
```

Isso irá:
1. 🦟 Consumir API InfoDengue (últimas 8 semanas epidemiológicas)
2. 💾 Armazenar RAW no MongoDB
3. 🔄 Transformar dados de dengue, zika e chikungunya
4. ✅ Persistir medições no PostgreSQL

**Processar dados RAW existentes:**
```bash
poetry run python scripts/process_raw_infodengue.py
```

---

## 📊 Endpoints da API

### 🏥 Health Check
- `GET /health` - Status da aplicação e conexões (MongoDB + PostgreSQL)

### 📏 Medições
- `GET /api/v1/measurements` - Lista medições com filtros
  - Query params: `indicator`, `source`, `territory`, `limit`, `offset`
- `GET /api/v1/measurements/latest` - Últimas medições por indicador
- `GET /api/v1/measurements/{id}` - Detalhes de uma medição específica

### 📡 Metadados
- `GET /api/v1/sources` - Lista fontes de dados
- `GET /api/v1/sources/status` - Status das fontes (última coleta, total medições)
- `GET /api/v1/indicators` - Lista indicadores disponíveis
- `GET /api/v1/territories` - Lista territórios cadastrados

### 🔄 Pipeline
- `GET /api/v1/pipeline/runs` - Histórico de execuções do pipeline
- `GET /api/v1/pipeline/runs/{id}` - Detalhes de uma execução

### 💡 Exemplos de Uso

```bash
# Últimas medições climáticas
curl http://localhost:8000/api/v1/measurements/latest

# Casos estimados de dengue (últimas 50 medições)
curl "http://localhost:8000/api/v1/measurements?indicator=dengue_casos_est&limit=50"

# Status das fontes de dados
curl http://localhost:8000/api/v1/sources/status

# Histórico de execuções do pipeline
curl http://localhost:8000/api/v1/pipeline/runs

# Health check
curl http://localhost:8000/health
```

---

## 📁 Estrutura do Projeto

```
NexoClima_Code/
├── backend/
│   ├── app/
│   │   ├── api/              # Rotas da API (v1/...)
│   │   │   ├── measurements.py
│   │   │   ├── sources.py
│   │   │   └── pipeline.py
│   │   ├── core/             # Configurações e logging
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── db/               # Conexões MongoDB/PostgreSQL
│   │   │   ├── mongodb.py
│   │   │   └── postgres.py
│   │   ├── domain/           # Modelos SQLAlchemy
│   │   │   └── models.py
│   │   ├── ingestion/        # Conectores de APIs externas
│   │   │   ├── base.py
│   │   │   ├── weather_connector.py
│   │   │   └── infodengue_connector.py
│   │   ├── transformation/   # Transformadores de dados
│   │   │   ├── weather_transformer.py
│   │   │   └── infodengue_transformer.py
│   │   ├── services/         # Lógica de negócio
│   │   │   └── pipeline_service.py
│   │   └── main.py           # Entry point FastAPI
│   ├── scripts/              # Scripts utilitários
│   │   ├── seed_initial_data.py
│   │   ├── add_epidemiology_data.py
│   │   ├── run_pipeline_manual.py
│   │   ├── run_infodengue_pipeline.py
│   │   └── process_raw_infodengue.py
│   ├── tests/                # Testes automatizados
│   ├── alembic/              # Migrações de banco
│   ├── pyproject.toml        # Dependências Poetry
│   └── .env                  # Variáveis de ambiente (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── Dashboard.tsx
│   │   │   ├── LatestMeasurements.tsx
│   │   │   ├── SourcesStatus.tsx
│   │   │   ├── WeatherChart.tsx
│   │   │   ├── EpidemiologyDashboard.tsx
│   │   │   └── Dashboard.css
│   │   ├── hooks/            # Custom hooks
│   │   │   ├── useMeasurements.ts
│   │   │   ├── useLatestMeasurements.ts
│   │   │   └── useSourcesStatus.ts
│   │   ├── services/         # API client
│   │   │   └── api.ts
│   │   ├── types/            # TypeScript types
│   │   │   └── index.ts
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 🔌 Fontes de Dados

### ☁️ Open-Meteo API
- **URL**: https://api.open-meteo.com/v1/forecast
- **Tipo**: Meteorologia
- **Dados**: Temperatura, precipitação, umidade, vento, código meteorológico
- **Frequência**: Horária
- **Cobertura**: Recife (lat: -8.05, lon: -34.9)
- **Documentação**: https://open-meteo.com/en/docs

### 🦟 InfoDengue API
- **URL**: https://info.dengue.mat.br/api/alertcity
- **Tipo**: Epidemiologia
- **Dados**: Casos de dengue, zika e chikungunya
- **Métricas**: Casos estimados, casos notificados, nível de alerta
- **Frequência**: Semanal (semanas epidemiológicas)
- **Fonte**: SINAN (Sistema de Informação de Agravos de Notificação)
- **Cobertura**: Recife (geocode: 2611606)
- **Documentação**: https://info.dengue.mat.br

### Indicadores Disponíveis

**Climáticos (7):**
- `temp_2m` - Temperatura a 2m (°C)
- `precipitation` - Precipitação (mm)
- `rain` - Chuva (mm)
- `precip_prob` - Probabilidade de Precipitação (%)
- `humidity` - Umidade Relativa (%)
- `wind_speed` - Velocidade do Vento (km/h)
- `weather_code` - Código Meteorológico (WMO)

**Epidemiológicos (11):**
- `dengue_casos_est` - Dengue: Casos Estimados
- `dengue_casos` - Dengue: Casos Notificados
- `dengue_nivel_alerta` - Dengue: Nível de Alerta (1-4)
- `chik_casos_est` - Chikungunya: Casos Estimados
- `chik_casos` - Chikungunya: Casos Notificados
- `chik_nivel_alerta` - Chikungunya: Nível de Alerta (1-4)
- `zika_casos_est` - Zika: Casos Estimados
- `zika_casos` - Zika: Casos Notificados
- `zika_nivel_alerta` - Zika: Nível de Alerta (1-4)
- `temp_media_epi` - Temperatura Média Epidemiológica (°C)
- `umidade_media_epi` - Umidade Média Epidemiológica (%)

**Níveis de Alerta:**
- 🟢 **1 - Verde**: Normal
- 🟡 **2 - Amarelo**: Atenção
- 🟠 **3 - Laranja**: Alerta
- 🔴 **4 - Vermelho**: Crítico

---

## 🧪 Testes

```bash
cd backend

# Executar todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov=app --cov-report=html

# Testes específicos
poetry run pytest tests/test_ingestion.py
poetry run pytest tests/test_transformation.py

# Ver relatório de cobertura
open htmlcov/index.html
```

---

## 📐 Princípios do Projeto

1. ❌ **NENHUM DADO MOCKADO** no fluxo funcional
2. ✅ **Rastreabilidade** total dos dados (fonte → RAW → CURATED)
3. ✅ **Idempotência** (pipeline pode ser reexecutado sem duplicação)
4. ✅ **Observabilidade** (logs estruturados, pipeline_runs)
5. ✅ **Separação de responsabilidades** (camadas claramente definidas)
6. ✅ **Validação de dados** (Pydantic em todas as camadas)
7. ✅ **Async/Await** para operações I/O

---

## 🔐 Segurança

- ✅ Variáveis sensíveis em `.env` (nunca commitadas)
- ✅ `.env` no `.gitignore`
- ✅ Validação de entrada com Pydantic
- ✅ CORS configurado para origens permitidas
- ✅ Rate limiting em APIs externas
- ✅ Logs estruturados para auditoria
- ✅ Conexões seguras (SSL) com MongoDB Atlas e Neon

---

## 📈 Roadmap

### ✅ Fase 1 - Concluída
- [x] Pipeline completo com Open-Meteo
- [x] Dashboard React com dados reais
- [x] Integração InfoDengue (epidemiologia)
- [x] Navegação por abas (Clima/Epidemiologia)
- [x] Gráficos interativos
- [x] UI moderna com gradientes e animações

### 📋 Próximas Fases
- [ ] **Autenticação e Autorização** (JWT)
- [ ] **Agendamento Automático** de pipelines (Celery/APScheduler)
- [ ] **Alertas Automáticos** via email/Telegram
- [ ] **Terceira fonte de dados** (Portal de Dados Abertos do Recife)
- [ ] **Machine Learning** para previsão de surtos
- [ ] **LLM Integration** para classificação e explicações
- [ ] **Servidor MCP** (Model Context Protocol)
- [ ] **Exportação** de relatórios (PDF/Excel)
- [ ] **API GraphQL** como alternativa ao REST
- [ ] **Mobile App** (React Native)
- [ ] **Docker Compose** para deploy simplificado
- [ ] **CI/CD** com GitHub Actions

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código
- **Python**: Black (formatação), Flake8 (linting), MyPy (type checking)
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

Projeto acadêmico - CESAR School - Disciplina Projetos 5

---

## 👥 Autores

**Secretaria de Saúde do Recife - Vigilância em Saúde / Vigidesastres**

- Desenvolvido para apoiar a vigilância de doenças relacionadas ao clima
- Integração de dados climáticos e epidemiológicos
- Foco em arboviroses: dengue, zika e chikungunya

---

## 🙏 Agradecimentos

- **Open-Meteo** - Dados climáticos de código aberto
- **InfoDengue/Fiocruz** - Dados epidemiológicos do Brasil
- **Ministério da Saúde** - SINAN e vigilância em saúde
- **MongoDB Atlas** - Plataforma NoSQL em nuvem
- **Neon** - PostgreSQL serverless
- **FastAPI** - Framework web moderno
- **React** - Biblioteca UI declarativa
- **Comunidade Open Source** - Ferramentas incríveis

---

## 📧 Contato

Para dúvidas ou sugestões, abra uma [issue](https://github.com/seu-usuario/nexoclima/issues) no GitHub.

---

## 🎓 Documentação Adicional

- [Arquitetura Detalhada](docs/architecture.md)
- [Pipeline de Dados](docs/data-pipeline.md)
- [Modelo de Banco de Dados](docs/database-model.md)
- [Guia de Desenvolvimento](docs/development-guide.md)
- [ADRs (Architecture Decision Records)](docs/decisions/)

---

<div align="center">

**Feito com ❤️ para a saúde pública**

⭐ Se este projeto foi útil, considere dar uma estrela!

</div>
