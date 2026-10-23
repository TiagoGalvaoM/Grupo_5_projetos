# ADR 001: Usar MongoDB Atlas para camada RAW

## Status
Aceito

## Contexto
O sistema NexoClima precisa consumir dados de múltiplas APIs externas com estruturas heterogêneas. É necessário armazenar os payloads originais para:
- Rastreabilidade e auditoria
- Reprocessamento em caso de mudança nas regras de transformação
- Debug de problemas na integração
- Prova de que dados reais foram consumidos

## Decisão
Utilizar **MongoDB Atlas** como camada de armazenamento RAW.

## Alternativas Consideradas

### 1. PostgreSQL com JSONB
**Prós**:
- Único banco de dados
- Queries SQL sobre JSON
- Sem custo adicional de infraestrutura

**Contras**:
- Schema rígido mesmo com JSONB
- Performance inferior para documentos grandes
- Complexidade de migrations para estruturas variáveis

### 2. Armazenamento de arquivos (S3, filesystem)
**Prós**:
- Simples
- Baixo custo

**Contras**:
- Sem índices
- Dificulta queries de auditoria
- Gestão de arquivos manual

### 3. MongoDB Atlas (escolhido)
**Prós**:
- Schema flexível para payloads heterogêneos
- Índices para queries rápidas
- Fácil armazenamento de metadados
- Managed service (backup automático)
- Free tier adequado para POC

**Contras**:
- Adiciona segundo banco ao stack
- Curva de aprendizado (pequena)

## Consequências

### Positivas
- Payloads originais preservados sem transformação
- Facilita adição de novas fontes sem modificar schema
- Permite reprocessamento completo do pipeline
- Índices permitem queries de auditoria eficientes
- Atlas gerencia backup e disponibilidade

### Negativas
- Necessário gerenciar conexões a dois bancos
- Desenvolvedores precisam conhecer MongoDB básico
- Custo futuro se volume crescer além do free tier

## Notas de Implementação
- Criar índices em: `source`, `collected_at`, `payload_hash`, `status`
- Usar `payload_hash` (SHA-256) para deduplicação
- Armazenar metadados da coleta junto com payload
- Manter referência (`raw_ingestion_id`) na camada CURATED

## Revisão
Esta decisão será revisada ao final da Fase 2, quando múltiplas fontes estiverem integradas.
