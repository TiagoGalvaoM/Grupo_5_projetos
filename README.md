# 🌡️ NexoClima Dashboard

  Sistema integrado de vigilância em saúde e clima para a Secretaria de
  Saúde do Recife.

  ## 📋 Sobre

  Plataforma que integra dados climáticos (Open-Meteo) e epidemiológicos
  (InfoDengue/SINAN) para monitorar correlações entre clima e arboviroses
  (dengue, zika, chikungunya).

  **Stack:** FastAPI + React + MongoDB Atlas + PostgreSQL (Neon)

  ## 🚀 Quick Start

  ### Backend
  ```bash
  cd backend
  poetry install
  poetry run alembic upgrade head
  poetry run python scripts/seed_initial_data.py
  poetry run python scripts/add_epidemiology_data.py
  poetry run uvicorn app.main:app --reload --port 8000

  Frontend

  cd frontend
  npm install
  npm run dev

  Acesse: http://localhost:5173

  ✨ Funcionalidades

  - 🌤️ Dados Climáticos: Temperatura, precipitação, umidade, vento
  (Open-Meteo)
  - 🦟 Dados Epidemiológicos: Casos e alertas de dengue, zika, chikungunya
  (InfoDengue)
  - 📊 Gráficos Interativos: Séries temporais e indicadores em tempo real
  - 🔄 Pipeline RAW → CURATED: Rastreabilidade completa dos dados
  - 🚨 Alertas por Níveis: Verde, Amarelo, Laranja, Vermelho

  🏗️ Arquitetura

  APIs Externas → Backend (FastAPI) → MongoDB (RAW) → Transformação →
  PostgreSQL (CURATED) → Frontend (React)

  📊 Executar Pipelines

  # Pipeline climático
  poetry run python scripts/run_pipeline_manual.py

  # Pipeline epidemiológico  
  poetry run python scripts/run_infodengue_pipeline.py

  📁 Estrutura

  NexoClima_Code/
  ├── backend/          # FastAPI + Python 3.12
  │   ├── app/          # API, modelos, pipeline
  │   └── scripts/      # Utilitários
  ├── frontend/         # React + TypeScript
  └── README.md

  🔌 Fontes de Dados

  - Open-Meteo: Meteorologia (https://open-meteo.com)
  - InfoDengue: Epidemiologia (https://info.dengue.mat.br)

  📝 Licença

  Projeto acadêmico - CESAR School - Disciplina Projetos 5
