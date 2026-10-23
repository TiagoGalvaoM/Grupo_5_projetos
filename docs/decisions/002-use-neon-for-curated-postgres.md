# ADR 002: Usar Neon PostgreSQL para camada CURATED

## Status
Aceito

## Contexto
A camada CURATED armazena dados transformados e estruturados. Precisa suportar:
- Modelo relacional normalizado
- Queries complexas (joins, agregações, séries temporais)
- Integridade referencial
- Potencialmente georreferenciamento (PostGIS)

## Decisão
Utilizar **Neon PostgreSQL** como banco de dados relacional para a camada CURATED.

## Alternativas Consideradas

### 1. PostgreSQL local/tradicional
**Prós**:
- Controle total
- Sem dependência de serviço externo

**Contras**:
- Gestão de servidor
- Backup manual
- Não adequado para projeto acadêmico

### 2. SQLite
**Prós**:
- Simples
- Zero configuração

**Contras**:
- Não adequado para produção
- Sem suporte a múltiplas conexões concorrentes
- Sem PostGIS

### 3. MySQL/MariaDB
**Prós**:
- Popular
- Bom desempenho

**Contras**:
- Suporte a JSON inferior ao PostgreSQL
- Sem PostGIS nativo

### 4. Neon PostgreSQL (escolhido)
**Prós**:
- PostgreSQL completo (compatibilidade total)
- Managed service (sem gestão de servidor)
- Free tier generoso
- Suporte a PostGIS (georreferenciamento)
- Serverless (escala automaticamente)
- Branching (útil para testes)

**Contras**:
- Dependência de serviço externo
- Limitações no free tier (armazenamento, compute)

## Consequências

### Positivas
- PostgreSQL é robusto e maduro
- Suporte a JSONB para metadados flexíveis
- PostGIS disponível para dados geográficos
- Alembic para migrations
- SQLAlchemy para ORM
- Managed service reduz overhead operacional

### Negativas
- Necessário connection string do Neon
- Limitações do free tier podem exigir upgrade no futuro

## Notas de Implementação
- Usar SQLAlchemy 2.0+ como ORM
- Alembic para versionamento de schema
- Índices em colunas de query frequente: `reference_time`, `indicator_id`, `source_id`, `territory_id`
- UNIQUE constraint para idempotência: `(source_id, indicator_id, territory_id, reference_time)`
- PostGIS será habilitado quando dados geográficos forem integrados

## Revisão
Esta decisão será revisada se limitações do Neon free tier se tornarem bloqueantes.
