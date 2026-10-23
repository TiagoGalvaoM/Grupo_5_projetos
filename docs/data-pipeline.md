# Pipeline de Dados - NexoClima

## Visão Geral

O pipeline de dados do NexoClima segue o princípio:

> **A principal automação acontece antes do dashboard**

```
Fonte Externa → Ingestão → RAW → Transformação → CURATED → API → Visualização
```

## Fluxo Detalhado

### 1. Coleta (Ingestão)

**Responsável**: `app/ingestion/`

**Processo**:
1. Scheduler aciona coleta (APScheduler)
2. Conector específico da fonte é executado
3. Request HTTP para API externa
4. Validação de resposta (status 200, JSON válido)
5. Criação de registro de ingestão com metadados

**Saída**:
```python
{
    "source": "open_meteo",
    "endpoint": "https://api.open-meteo.com/v1/forecast",
    "request_params": {...},
    "collected_at": "2024-10-23T12:00:00Z",
    "reference_period": {
        "start": "2024-10-23T00:00:00Z",
        "end": "2024-10-24T00:00:00Z"
    },
    "status": "success",
    "http_status": 200,
    "payload": {...},  # Resposta original da API
    "payload_hash": "sha256...",
    "pipeline_version": "0.1.0"
}
```

---

### 2. Armazenamento RAW (MongoDB Atlas)

**Responsável**: `app/db/mongodb.py`

**Objetivo**:
- Preservar payload original sem transformação
- Rastreabilidade completa
- Permitir reprocessamento
- Auditoria

**Coleção**: `raw_ingestions`

**Índices**:
- `{source: 1, collected_at: -1}`
- `{payload_hash: 1}` (deduplicação)
- `{status: 1, collected_at: -1}`

**Em caso de erro**:
```python
{
    "source": "open_meteo",
    "collected_at": "2024-10-23T12:00:00Z",
    "status": "error",
    "http_status": 500,
    "error_type": "HTTPError",
    "error_message": "Connection timeout",
    "retry_count": 3
}
```

---

### 3. Transformação (ETL)

**Responsável**: `app/transformation/`

**Entrada**: Documento RAW do MongoDB
**Saída**: Lista de objetos `Measurement` (modelo de domínio)

**Etapas**:

#### 3.1. Validação
- Schema do payload corresponde ao esperado
- Campos obrigatórios presentes
- Tipos corretos

#### 3.2. Normalização
- **Timestamps**: Conversão para UTC, ISO 8601
- **Timezone**: Padronização (America/Recife → UTC)
- **Valores nulos**: Tratamento explícito (None, skip, ou valor padrão)
- **Unidades**: Conversão se necessário (ex: Fahrenheit → Celsius)

#### 3.3. Padronização
- Mapeamento de campos da fonte para modelo interno
- Criação de `indicator_code` padronizado
- Resolução de territorialidade (coordenadas → território)

#### 3.4. Deduplicação
- Chave lógica: `(source, indicator, territory, reference_time)`
- Estratégia: Upsert (insert ou update se já existe)

**Modelo interno (Measurement)**:
```python
class Measurement:
    source_id: int
    indicator_id: int
    territory_id: int | None
    reference_time: datetime
    collected_at: datetime
    value: float
    unit: str
    raw_ingestion_id: str  # Referência ao MongoDB
    metadata: dict | None
```

**Transformador específico**: `app/transformation/weather_transformer.py`

---

### 4. Persistência CURATED (Neon PostgreSQL)

**Responsável**: `app/db/postgres.py`, `app/services/measurement_service.py`

**Tabelas envolvidas**:
- `data_sources`: Cadastro de fontes
- `indicators`: Cadastro de indicadores
- `territories`: Cadastro de territórios
- `measurements`: Medições transformadas
- `pipeline_runs`: Log de execuções

**Estratégia de escrita**:
- Upsert por chave lógica (evita duplicação)
- Transação atômica por lote de medições
- Registro de `pipeline_run` em paralelo

---

### 5. Classificação (Opcional nesta fase)

**Responsável**: `app/classification/`

**Entrada**: Measurement do banco
**Saída**: Classification

**Método inicial**: Regras determinísticas

**Exemplo conceitual** (limiares a validar com cliente):
```python
if measurement.indicator == "precipitation" and measurement.value >= 50:
    classification = "critico"
elif measurement.value >= 20:
    classification = "atencao"
else:
    classification = "normal"
```

⚠️ **IMPORTANTE**: Limiares acima são apenas exemplos. Não usar em produção sem validação do cliente.

---

### 6. Exposição via API

**Responsável**: `app/api/v1/`

**Endpoints**:
- `GET /api/v1/measurements`: Consulta medições
  - Filtros: `source`, `indicator`, `start`, `end`, `territory`
- `GET /api/v1/measurements/latest`: Últimas medições por indicador
- `GET /api/v1/sources/status`: Status das fontes de dados
- `GET /api/v1/pipeline/runs`: Histórico de execuções

---

## Idempotência

**Problema**: Evitar inserção duplicada ao reexecutar pipeline

**Solução**:
1. **Camada RAW**: Hash do payload como índice único
   - Se hash já existe, skip insert
2. **Camada CURATED**: Upsert por chave lógica
   - `UNIQUE (source_id, indicator_id, territory_id, reference_time)`
   - `ON CONFLICT DO UPDATE` ou `ON CONFLICT DO NOTHING`

**Vantagem**: Pipeline pode ser reexecutado sem efeitos colaterais

---

## Observabilidade

Cada execução do pipeline registra:

```python
class PipelineRun:
    id: UUID
    source_id: int
    started_at: datetime
    finished_at: datetime | None
    status: "running" | "success" | "error"
    raw_records: int
    processed_records: int
    error_records: int
    error_message: str | None
    duration_seconds: float | None
```

**Logs estruturados**:
```python
logger.info("pipeline_started", source="open_meteo", run_id=run_id)
logger.info("ingestion_completed", records=150, duration=2.3)
logger.info("transformation_completed", valid=148, invalid=2)
logger.error("transformation_failed", error=str(e), record=record_id)
```

---

## Agendamento

**Tecnologia**: APScheduler

**Frequência inicial**: A cada 60 minutos (configurável via `.env`)

**Estratégia**:
- Cada fonte tem seu próprio job
- Jobs independentes (falha em uma fonte não bloqueia outras)
- Registro de cada execução em `pipeline_runs`

**Exemplo de configuração**:
```python
scheduler.add_job(
    func=run_weather_pipeline,
    trigger="interval",
    minutes=60,
    id="weather_pipeline",
    replace_existing=True
)
```

---

## Tratamento de Falhas

### Falha na Ingestão (API externa indisponível)

```
API Fail → Registrar RAW com status="error"
         → Registrar pipeline_run com status="error"
         → Não apagar último dado válido
         → Dashboard mostra "Fonte indisponível desde <timestamp>"
```

### Falha na Transformação (payload inesperado)

```
Invalid payload → Log detalhado do erro
               → Registro em pipeline_run.error_records
               → Continuar processamento de registros válidos
               → Alertar via log
```

### Falha no banco CURATED

```
DB error → Rollback de transação
         → Registrar pipeline_run com status="error"
         → RAW permanece intacto para retry
```

**Estratégia de retry**: A implementar (exemplo: 3 tentativas com backoff exponencial)

---

## Proveniência do Dado

Todo dado exibido no dashboard deve permitir rastrear:

1. **Qual fonte?** → `data_sources.name`
2. **Quando foi coletado?** → `measurements.collected_at`
3. **Qual período representa?** → `measurements.reference_time`
4. **Qual transformação?** → `pipeline_runs.id`, `version`
5. **Payload original?** → `measurements.raw_ingestion_id` → MongoDB

**Exemplo de query de rastreamento**:
```sql
SELECT
    m.value,
    m.reference_time,
    m.collected_at,
    ds.name as source_name,
    i.name as indicator_name,
    m.raw_ingestion_id
FROM measurements m
JOIN data_sources ds ON m.source_id = ds.id
JOIN indicators i ON m.indicator_id = i.id
WHERE m.id = <measurement_id>;
```

Com `raw_ingestion_id`, buscar payload original no MongoDB.

---

## Diagrama de Sequência

```
┌────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│Scheduler│     │Connector │     │ MongoDB │     │Transform │     │PostgreSQL│
└───┬────┘     └────┬─────┘     └────┬────┘     └────┬─────┘     └────┬─────┘
    │               │                │                │                │
    │ trigger()     │                │                │                │
    ├──────────────>│                │                │                │
    │               │ GET API        │                │                │
    │               ├───────────────>│                │                │
    │               │ JSON response  │                │                │
    │               │<───────────────│                │                │
    │               │ insert RAW     │                │                │
    │               ├───────────────>│                │                │
    │               │ doc_id         │                │                │
    │               │<───────────────│                │                │
    │               │                │ fetch RAW      │                │
    │               │                │<───────────────│                │
    │               │                │ payload        │                │
    │               │                ├───────────────>│                │
    │               │                │                │ upsert()       │
    │               │                │                ├───────────────>│
    │               │                │                │ rows affected  │
    │               │                │                │<───────────────│
```

---

## Primeira Vertical Slice - Checklist

- [ ] Conector Open-Meteo funcional
- [ ] Ingestão persiste RAW no MongoDB Atlas
- [ ] Transformação converte payload para modelo interno
- [ ] Dados tratados persistidos no Neon
- [ ] API retorna medições reais
- [ ] Dashboard consome API
- [ ] Agendamento automático funcionando
- [ ] Logs estruturados em todas as etapas
- [ ] Tratamento de erro registrado
- [ ] Proveniência rastreável

---

## Próximos Passos

1. Implementar segunda fonte (dados abertos Recife)
2. Adicionar integração por território
3. Implementar classificação com regras validadas
4. Adicionar alertas
5. Integração com LLM
6. Servidor MCP
