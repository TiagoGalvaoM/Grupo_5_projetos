# ADR 005: Implementar MCP após pipeline core funcional

## Status
Aceito

## Contexto
O projeto mencionou o uso de MCP (Model Context Protocol) para expor funcionalidades do NexoClima. É necessário definir quando e como implementar.

## Decisão
Implementar **MCP Server somente após o pipeline core estar funcional** (Fase 7).

Pipeline core = Ingestão → RAW → Transformação → CURATED → API → Dashboard

## Alternativas Consideradas

### 1. Implementar MCP desde o início
**Prós**:
- Funcionalidade completa desde o princípio

**Contras**:
- Adiciona complexidade prematuramente
- MCP sem dados reais não demonstra valor
- Desvia foco da primeira vertical slice

### 2. Implementar MCP após core (escolhido)
**Prós**:
- Prioriza entrega de valor (dados reais no dashboard)
- MCP com dados reais é mais demonstrável
- Permite entender quais tools são realmente úteis
- Sistema funciona independentemente de MCP

**Contras**:
- MCP fica para depois

## Consequências

### Positivas
- Foco na primeira vertical slice (dados reais no dashboard)
- MCP será implementado com conhecimento do que realmente é útil expor
- Evita overengineering prematuro

### Negativas
- MCP não estará disponível nas primeiras fases

## Roadmap

### Fase 1-4: Core Pipeline
- Ingestão de dados reais
- Transformação
- Persistência
- API REST
- Dashboard

### Fase 5-6: Classificação e LLM
- Regras de classificação
- Explicações via LLM

### Fase 7: MCP Server
- Criação do servidor MCP
- Exposição de tools controladas

## MCP Tools Planejadas

Quando implementado, o MCP Server do NexoClima poderá expor:

```python
# Possíveis tools MCP
- get_latest_weather(territory: str) -> dict
- get_source_status(source_name: str) -> dict
- get_measurements(indicator: str, start: str, end: str) -> list
- get_classifications(territory: str, level: str) -> list
- get_pipeline_runs(limit: int) -> list
- get_summary_context(territory: str, period: str) -> str
```

## Princípios de Segurança MCP

Quando implementado:
- ❌ Sem SQL arbitrário via MCP
- ✅ Tools com schemas Pydantic validados
- ✅ Parâmetros validados
- ✅ Queries controladas (não permitir injeção)
- ✅ Limites de resultados (ex: max 1000 registros)
- ✅ Rate limiting se necessário

## Notas de Implementação

```python
# Estrutura futura
app/mcp/
├── __init__.py
├── server.py          # MCP Server
├── tools.py           # Definição de tools
└── schemas.py         # Schemas de input/output
```

## Revisão
Esta decisão será revisada ao final da Fase 6, quando classificação e LLM estiverem funcionais.
