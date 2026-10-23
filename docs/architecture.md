# Arquitetura NexoClima

## Visão Geral

NexoClima é um sistema de integração, transformação e visualização de dados heterogêneos para apoiar a Vigilância em Saúde / Vigidesastres da Secretaria de Saúde do Recife.

## Problema

O desafio não é apenas visualizar dados, mas sim:
- Consumir dados reais de fontes externas
- Automatizar a coleta
- Armazenar dados brutos para rastreabilidade
- Transformar e padronizar dados heterogêneos
- Integrar fontes diferentes
- Persistir dados tratados em banco relacional
- Classificar situações de interesse
- Disponibilizar dados reais em dashboard
- Permitir uso de LLM sobre dados reais
- Expor funções via MCP

## Princípio Arquitetural

**Arquitetura cliente-servidor em camadas com backend monolítico modular.**

```
┌─────────────────┐
│  Fontes Externas│ (APIs públicas, CKAN, datasets)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   INGESTÃO      │ (Conectores por fonte)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MongoDB Atlas   │ (RAW - Dados brutos)
│   (RAW Layer)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TRANSFORMAÇÃO   │ (ETL, normalização, validação)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Neon PostgreSQL │ (CURATED - Dados tratados)
│ (CURATED Layer) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CLASSIFICAÇÃO   │ (Regras determinísticas)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Interna   │ (FastAPI - REST)
└────────┬────────┘
         │
         ├────────────────┐
         │                │
         ▼                ▼
┌─────────────┐   ┌──────────┐
│  Dashboard  │   │   LLM    │
│   (React)   │   │   MCP    │
└─────────────┘   └──────────┘
```

## Camadas

### 1. Camada de Ingestão
- **Responsabilidade**: Consumir APIs externas e fontes de dados
- **Tecnologia**: Python + httpx
- **Padrão**: Um conector por fonte
- **Saída**: Payload bruto + metadados

### 2. Camada RAW (MongoDB Atlas)
- **Responsabilidade**: Armazenar dados originais sem transformação
- **Objetivo**: Rastreabilidade, auditoria, reprocessamento
- **Coleção principal**: `raw_ingestions`
- **Metadados**: source, timestamp, status, hash

### 3. Camada de Transformação
- **Responsabilidade**: ETL, normalização, validação
- **Entrada**: Dados brutos do MongoDB
- **Saída**: Modelos de domínio padronizados
- **Processo**:
  - Validação de tipos
  - Normalização de timestamps/timezone
  - Padronização de unidades
  - Resolução de territorialidade
  - Deduplicação

### 4. Camada CURATED (Neon PostgreSQL)
- **Responsabilidade**: Armazenar dados estruturados e tratados
- **Modelo**: Relacional normalizado
- **Tabelas principais**: data_sources, indicators, territories, measurements, classifications, pipeline_runs

### 5. Camada de Classificação
- **Responsabilidade**: Aplicar regras de negócio e classificar situações
- **Método**: Regras determinísticas (inicialmente)
- **Evolução**: Regras validadas pelo cliente

### 6. Camada de API
- **Responsabilidade**: Expor dados tratados
- **Tecnologia**: FastAPI
- **Endpoints**: `/api/v1/measurements`, `/api/v1/sources`, `/api/v1/pipeline/runs`

### 7. Camada de Apresentação
- **Responsabilidade**: Visualização de dados
- **Tecnologia**: React + TypeScript + Vite
- **Requisito**: Apenas dados reais

### 8. Camada de IA (Futura)
- **LLM**: Geração de resumos e explicações
- **MCP**: Exposição de ferramentas de consulta
- **Princípio**: Sistema deve funcionar sem IA

## Decisões Arquiteturais

Ver ADRs em `docs/decisions/`

### Por que MongoDB Atlas para RAW?
- Schema flexível para payloads heterogêneos
- Preservação do formato original
- Facilidade de armazenar metadados
- Reprocessamento simplificado

### Por que Neon PostgreSQL para CURATED?
- Modelo relacional para dados estruturados
- Queries complexas por tempo, território, indicador
- Integridade referencial
- Suporte a PostGIS (georreferenciamento)

### Por que monólito modular?
- Projeto acadêmico com equipe pequena
- Facilidade de demonstração
- Baixo overhead operacional
- Migração futura para microsserviços facilitada pela modularização

## Fluxo de Dados - Primeira Vertical Slice

```
Open-Meteo API
    ↓ (HTTP Request)
MongoDB Atlas RAW
    ↓ (ETL)
Neon PostgreSQL CURATED
    ↓ (Query)
FastAPI
    ↓ (REST)
Dashboard React
```

## Princípios de Design

1. **Dados Reais**: Nenhum dado mockado no fluxo funcional
2. **Rastreabilidade**: Todo dado deve ter proveniência clara
3. **Idempotência**: Pipeline não duplica dados
4. **Observabilidade**: Logs estruturados em todas as camadas
5. **Separação de Responsabilidades**: Cada camada com objetivo único
6. **Extensibilidade**: Adicionar novas fontes sem modificar core

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.12, FastAPI, Pydantic |
| Ingestão | httpx |
| RAW | MongoDB Atlas |
| Transformação | Pandas (quando necessário) |
| CURATED | PostgreSQL (Neon), SQLAlchemy |
| Migrações | Alembic |
| Scheduler | APScheduler |
| Frontend | React, TypeScript, Vite |
| Testes | pytest |

## Próximas Fases

1. ✅ **Fase 1**: Uma fonte meteorológica real (Open-Meteo)
2. **Fase 2**: Segunda fonte (Dados abertos Recife)
3. **Fase 3**: Fonte de saúde pública
4. **Fase 4**: Integração por tempo e território
5. **Fase 5**: Classificação com regras validadas
6. **Fase 6**: LLM para resumos
7. **Fase 7**: MCP Server
