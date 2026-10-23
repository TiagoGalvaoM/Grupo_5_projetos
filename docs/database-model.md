# Modelo de Dados - NexoClima

## Camadas de Dados

### 1. RAW (MongoDB Atlas)
Dados brutos sem transformação

### 2. CURATED (Neon PostgreSQL)
Dados estruturados e normalizados

---

## MongoDB Atlas - Camada RAW

### Coleção: `raw_ingestions`

Armazena o retorno original das APIs externas.

**Schema** (conceitual - MongoDB é schemaless):

```javascript
{
  _id: ObjectId,
  source: String,              // Nome da fonte (ex: "open_meteo")
  endpoint: String,            // URL completa chamada
  request_params: Object,      // Parâmetros da request
  collected_at: ISODate,       // Timestamp UTC da coleta
  reference_period: {
    start: ISODate,            // Início do período de dados
    end: ISODate               // Fim do período de dados
  },
  status: String,              // "success" | "error"
  http_status: Number,         // 200, 404, 500, etc
  payload: Object,             // Resposta original da API
  payload_hash: String,        // SHA-256 do payload (deduplicação)
  pipeline_version: String,    // Versão do pipeline (ex: "0.1.0")
  error_type: String,          // Tipo de erro (se status="error")
  error_message: String,       // Mensagem de erro
  retry_count: Number,         // Número de tentativas
  created_at: ISODate          // Timestamp de criação do registro
}
```

**Índices**:
```javascript
{source: 1, collected_at: -1}      // Query por fonte e tempo
{payload_hash: 1}                   // Deduplicação
{status: 1, collected_at: -1}       // Monitoring
{reference_period.start: 1}         // Query por período
```

**Exemplo de documento (sucesso)**:
```json
{
  "_id": "671234567890abcdef123456",
  "source": "open_meteo",
  "endpoint": "https://api.open-meteo.com/v1/forecast",
  "request_params": {
    "latitude": -8.05,
    "longitude": -34.9,
    "hourly": "temperature_2m,precipitation",
    "timezone": "America/Recife"
  },
  "collected_at": "2024-10-23T15:00:00Z",
  "reference_period": {
    "start": "2024-10-23T00:00:00Z",
    "end": "2024-10-24T00:00:00Z"
  },
  "status": "success",
  "http_status": 200,
  "payload": {
    "latitude": -8.05,
    "longitude": -34.9,
    "hourly": {
      "time": ["2024-10-23T00:00", "2024-10-23T01:00"],
      "temperature_2m": [24.5, 24.1],
      "precipitation": [0.0, 0.2]
    }
  },
  "payload_hash": "a3f5d8c...",
  "pipeline_version": "0.1.0",
  "created_at": "2024-10-23T15:00:01Z"
}
```

---

## PostgreSQL (Neon) - Camada CURATED

### ERD Simplificado

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│  data_sources   │       │   indicators     │       │  territories    │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)          │       │ id (PK)         │
│ name            │       │ code             │       │ code            │
│ provider        │       │ name             │       │ name            │
│ source_type     │       │ category         │       │ type            │
│ url             │       │ unit             │       │ latitude        │
│ active          │       │ description      │       │ longitude       │
│ created_at      │       └──────────────────┘       │ geometry        │
└─────────────────┘                                  └─────────────────┘
         │                        │                            │
         │                        │                            │
         │         ┌──────────────┴────────────────────────────┘
         │         │                        │
         │         │                        │
         ▼         ▼                        ▼
     ┌────────────────────────────────────────────┐
     │            measurements                     │
     ├────────────────────────────────────────────┤
     │ id (PK)                                     │
     │ source_id (FK → data_sources)               │
     │ indicator_id (FK → indicators)              │
     │ territory_id (FK → territories, nullable)   │
     │ reference_time                              │
     │ collected_at                                │
     │ value                                       │
     │ unit                                        │
     │ raw_ingestion_id (ref MongoDB)              │
     │ metadata (jsonb)                            │
     │ created_at                                  │
     │ UNIQUE(source_id, indicator_id,             │
     │        territory_id, reference_time)        │
     └────────────────────────────────────────────┘
                    │
                    │
                    ▼
            ┌──────────────────┐
            │  classifications │
            ├──────────────────┤
            │ id (PK)          │
            │ measurement_id   │
            │ type             │
            │ label            │
            │ score            │
            │ rule_version     │
            │ classified_at    │
            └──────────────────┘

     ┌────────────────────────┐
     │    pipeline_runs       │
     ├────────────────────────┤
     │ id (PK)                │
     │ source_id (FK)         │
     │ started_at             │
     │ finished_at            │
     │ status                 │
     │ raw_records            │
     │ processed_records      │
     │ error_records          │
     │ error_message          │
     └────────────────────────┘
```

---

### Tabela: `data_sources`

Cadastro de fontes de dados externas.

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    provider VARCHAR(255),
    source_type VARCHAR(50),  -- 'api', 'ckan', 'csv', 'manual'
    url TEXT,
    update_frequency VARCHAR(50),  -- 'hourly', 'daily', 'weekly'
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Dados iniciais**:
```sql
INSERT INTO data_sources (name, provider, source_type, url, update_frequency)
VALUES ('open_meteo', 'Open-Meteo', 'api', 'https://api.open-meteo.com', 'hourly');
```

---

### Tabela: `indicators`

Catálogo de indicadores/variáveis medidas.

```sql
CREATE TABLE indicators (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,  -- 'temp_2m', 'precip_hourly'
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),  -- 'meteorology', 'health', 'environmental'
    unit VARCHAR(50),  -- 'celsius', 'mm', 'percent'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Dados iniciais** (meteorologia):
```sql
INSERT INTO indicators (code, name, category, unit, description) VALUES
('temp_2m', 'Temperatura a 2m', 'meteorology', 'celsius', 'Temperatura do ar a 2 metros'),
('precipitation', 'Precipitação', 'meteorology', 'mm', 'Precipitação acumulada'),
('rain', 'Chuva', 'meteorology', 'mm', 'Chuva'),
('precip_prob', 'Probabilidade de Precipitação', 'meteorology', 'percent', NULL),
('humidity', 'Umidade Relativa', 'meteorology', 'percent', 'Umidade relativa do ar'),
('wind_speed', 'Velocidade do Vento', 'meteorology', 'km/h', 'Velocidade do vento a 10m'),
('weather_code', 'Código Meteorológico', 'meteorology', 'wmo_code', 'Código WMO');
```

---

### Tabela: `territories`

Cadastro de territórios (cidade, bairros, regionais).

```sql
CREATE TABLE territories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE,  -- Código oficial (IBGE, etc)
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),  -- 'city', 'neighborhood', 'regional', 'state'
    parent_id INTEGER REFERENCES territories(id),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    geometry GEOMETRY(GEOMETRY, 4326),  -- PostGIS (opcional)
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Dados iniciais**:
```sql
INSERT INTO territories (code, name, type, latitude, longitude) VALUES
('2611606', 'Recife', 'city', -8.05, -34.9);
```

---

### Tabela: `measurements`

Medições transformadas (núcleo do sistema).

```sql
CREATE TABLE measurements (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES data_sources(id),
    indicator_id INTEGER NOT NULL REFERENCES indicators(id),
    territory_id INTEGER REFERENCES territories(id),
    reference_time TIMESTAMP NOT NULL,  -- Timestamp da medição
    collected_at TIMESTAMP NOT NULL,    -- Timestamp da coleta
    value NUMERIC(15, 5) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    raw_ingestion_id VARCHAR(24),  -- ObjectId do MongoDB
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, indicator_id, territory_id, reference_time)
);

CREATE INDEX idx_measurements_time ON measurements(reference_time DESC);
CREATE INDEX idx_measurements_source ON measurements(source_id);
CREATE INDEX idx_measurements_indicator ON measurements(indicator_id);
CREATE INDEX idx_measurements_territory ON measurements(territory_id);
CREATE INDEX idx_measurements_collected ON measurements(collected_at DESC);
```

**Constraint de idempotência**: `UNIQUE(source_id, indicator_id, territory_id, reference_time)`

---

### Tabela: `pipeline_runs`

Log de execuções do pipeline.

```sql
CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id INTEGER NOT NULL REFERENCES data_sources(id),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- 'running', 'success', 'error'
    raw_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    error_records INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds NUMERIC(10, 3),
    pipeline_version VARCHAR(20),
    metadata JSONB
);

CREATE INDEX idx_pipeline_runs_source ON pipeline_runs(source_id, started_at DESC);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status, started_at DESC);
```

---

### Tabela: `classifications`

Classificações de medições (Fase 2).

```sql
CREATE TABLE classifications (
    id BIGSERIAL PRIMARY KEY,
    measurement_id BIGINT NOT NULL REFERENCES measurements(id),
    classification_type VARCHAR(100) NOT NULL,  -- 'risk_level', 'alert_level'
    label VARCHAR(100) NOT NULL,  -- 'normal', 'atencao', 'critico'
    score NUMERIC(5, 2),  -- Score numérico se aplicável
    rule_version VARCHAR(20),  -- Versão das regras aplicadas
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_classifications_measurement ON classifications(measurement_id);
CREATE INDEX idx_classifications_label ON classifications(label, classified_at DESC);
```

---

## Queries Comuns

### Últimas medições por indicador
```sql
SELECT DISTINCT ON (i.code)
    i.code,
    i.name,
    m.value,
    m.unit,
    m.reference_time,
    m.collected_at
FROM measurements m
JOIN indicators i ON m.indicator_id = i.id
WHERE m.territory_id = (SELECT id FROM territories WHERE code = '2611606')
ORDER BY i.code, m.reference_time DESC;
```

### Série temporal de precipitação
```sql
SELECT
    reference_time,
    value,
    unit
FROM measurements
WHERE indicator_id = (SELECT id FROM indicators WHERE code = 'precipitation')
  AND territory_id = (SELECT id FROM territories WHERE code = '2611606')
  AND reference_time >= NOW() - INTERVAL '7 days'
ORDER BY reference_time ASC;
```

### Status das fontes
```sql
SELECT
    ds.name,
    ds.active,
    MAX(pr.started_at) as last_run,
    pr.status as last_status,
    COUNT(DISTINCT m.id) as total_measurements
FROM data_sources ds
LEFT JOIN pipeline_runs pr ON ds.id = pr.source_id
LEFT JOIN measurements m ON ds.id = m.source_id
GROUP BY ds.id, ds.name, ds.active, pr.status
ORDER BY last_run DESC;
```

### Rastreamento de proveniência
```sql
SELECT
    m.value,
    m.unit,
    m.reference_time,
    ds.name as source,
    i.name as indicator,
    t.name as territory,
    m.collected_at,
    m.raw_ingestion_id,
    pr.id as pipeline_run_id
FROM measurements m
JOIN data_sources ds ON m.source_id = ds.id
JOIN indicators i ON m.indicator_id = i.id
LEFT JOIN territories t ON m.territory_id = t.id
LEFT JOIN pipeline_runs pr ON pr.source_id = ds.id
    AND pr.started_at <= m.collected_at
    AND pr.finished_at >= m.collected_at
WHERE m.id = $1;
```

---

## Migrações (Alembic)

As migrações serão gerenciadas pelo Alembic.

**Estrutura**:
```
backend/alembic/
├── env.py
├── script.py.mako
├── alembic.ini
└── versions/
    ├── 001_initial_schema.py
    └── ...
```

**Comandos**:
```bash
# Criar migração
alembic revision --autogenerate -m "initial schema"

# Aplicar migrações
alembic upgrade head

# Reverter
alembic downgrade -1
```

---

## Evolução do Modelo

### Fase 1 (Atual)
- Fonte única: Open-Meteo
- Território único: Recife (coordenadas)
- Indicadores: meteorológicos

### Fase 2
- Múltiplas fontes
- Territórios: bairros, regionais
- Classificações: regras de risco

### Fase 3
- Indicadores de saúde
- Correlações entre fontes
- Agregações temporais

### Fase 4
- Alertas automáticos
- Histórico de alertas
- Integração LLM

---

## Considerações de Performance

1. **Particionamento** (futuro): Por `reference_time` (mensal)
2. **Índices**: Criados nas colunas de query frequente
3. **Agregações**: Considerar tabelas materializadas para dashboards
4. **Archival**: Política de retenção a definir (ex: RAW 90 dias, CURATED permanente)

---

## Backup e Disaster Recovery

- **MongoDB Atlas**: Backup automático (configuração do Atlas)
- **Neon PostgreSQL**: Backup automático (configuração do Neon)
- **Reprocessamento**: RAW permite recriar CURATED se necessário
