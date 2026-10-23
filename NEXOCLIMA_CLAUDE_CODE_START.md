# NexoClima — Instruções para início do desenvolvimento no Claude Code

## 0. Contexto

Você está iniciando o desenvolvimento do **NexoClima**, projeto acadêmico da disciplina **Projetos 5 — Sistemas de Informação — CESAR School**.

O cliente/contexto do projeto é a **Vigilância em Saúde / Vigidesastres da Secretaria de Saúde do Recife**.

O problema principal identificado não é apenas a visualização dos dados. O foco do projeto é:

- consumir dados reais de fontes externas;
- automatizar a coleta;
- armazenar o dado bruto;
- transformar e padronizar dados heterogêneos;
- integrar fontes diferentes;
- persistir dados tratados em banco relacional;
- classificar situações de interesse;
- disponibilizar dados reais em um dashboard;
- permitir uso de LLM sobre dados reais;
- expor funções e consultas através de MCP.

O professor deixou claro que, ao final do projeto, deseja ver:

1. **Bancos de dados reais**;
2. **Consumo de APIs reais**;
3. **Construção de dashboard com dados reais**;
4. **Nenhum dado mockado como base da aplicação final**.

Foi desenhado em sala um fluxo semelhante a:

```text
API → ATLAS → T → NEON → CLASSIFICAR → LLM / MCP
```

### Hipótese de interpretação deste fluxo

Até validação posterior com o professor, assumir:

- **API** = fonte externa real;
- **ATLAS** = MongoDB Atlas, usado como camada de ingestão/raw;
- **T** = Transformação/ETL;
- **NEON** = PostgreSQL hospedado no Neon, usado como camada estruturada/curada;
- **CLASSIFICAR** = regras de classificação de risco/situação;
- **LLM** = geração de explicações, resumos e consultas em linguagem natural;
- **MCP** = Model Context Protocol para expor ferramentas/recursos do NexoClima a um cliente de IA.

Essa interpretação é uma decisão inicial de projeto, não uma afirmação de que foi exatamente isso que o professor quis dizer.

---

# 1. Regra principal do projeto

## NÃO UTILIZAR DADOS MOCKADOS COMO FONTE DA APLICAÇÃO

É permitido usar fixtures apenas em testes automatizados unitários.

Não criar:

- arrays fixos fingindo resposta de API;
- JSONs inventados para alimentar dashboard;
- registros fictícios no banco para demonstrar funcionalidades;
- gráficos preenchidos manualmente.

Toda tela funcional deve ser alimentada por dados provenientes de uma **fonte real**, passando pelo pipeline real.

Se alguma funcionalidade ainda não possuir uma fonte real disponível:

1. deixar a funcionalidade incompleta ou desabilitada;
2. documentar a dependência;
3. não inventar dados.

---

# 2. Objetivo técnico da primeira POC

A primeira POC deve provar o seguinte fluxo ponta a ponta:

```text
API REAL
   ↓
COLETA AUTOMÁTICA
   ↓
MONGODB ATLAS — RAW
   ↓
TRANSFORMAÇÃO / PADRONIZAÇÃO
   ↓
NEON POSTGRES — CURATED
   ↓
API INTERNA DO NEXOCLIMA
   ↓
DASHBOARD
```

Depois que esse fluxo estiver funcionando, evoluir para:

```text
NEON
  ↓
CLASSIFICAÇÃO
  ↓
LLM
  ↓
MCP
```

O objetivo inicial NÃO é implementar todas as funcionalidades imaginadas do produto.

O objetivo é provar que o pipeline de dados real funciona.

---

# 3. Princípio arquitetural

Utilizar uma arquitetura **cliente-servidor em camadas**, com backend organizado como **monólito modular**.

Separar claramente:

```text
Fontes externas
      ↓
Ingestão
      ↓
Raw storage
      ↓
Transformação
      ↓
Persistência curada
      ↓
Domínio / classificação
      ↓
API
      ↓
Frontend
      ↓
IA / MCP
```

Evitar microsserviços nesta fase.

O projeto é acadêmico, possui equipe pequena e ainda está em POC/MVP.

A arquitetura deve priorizar:

- clareza;
- rastreabilidade;
- baixo acoplamento;
- facilidade de demonstrar o fluxo;
- facilidade de adicionar novas fontes futuramente.

---

# 4. Stack inicial recomendada

## Backend

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy ou SQLModel
- Alembic
- httpx
- pandas quando necessário
- PyMongo / MongoDB driver
- psycopg / driver compatível com Neon

## Banco RAW

**MongoDB Atlas**

Objetivo:

- armazenar payloads recebidos das APIs sem perder o formato original;
- manter rastreabilidade;
- permitir reprocessamento;
- registrar metadados da coleta.

## Banco CURATED

**Neon PostgreSQL**

Objetivo:

- armazenar dados transformados;
- modelo relacional;
- consultas para o dashboard;
- classificação;
- histórico;
- joins por tempo, território, indicador e fonte.

## Georreferenciamento

Se necessário:

- PostGIS, caso disponível na configuração utilizada;
- GeoJSON;
- latitude/longitude;
- códigos territoriais padronizados.

## Frontend

- React
- TypeScript
- Vite
- biblioteca de gráficos adequada;
- biblioteca de mapas apenas quando existir dado geográfico real.

## IA

Criar uma camada desacoplada para LLM.

Não acoplar regras de negócio principais ao modelo.

O sistema deve continuar funcionando sem LLM.

## MCP

Criar um servidor MCP em fase posterior para expor ferramentas de consulta do NexoClima.

---

# 5. Fontes reais — primeira prioridade

Não começar pelo frontend.

Começar encontrando e validando fontes reais.

## Fonte 1 — Meteorologia

Priorizar uma API real de clima/precipitação.

Uma opção inicial aceitável para POC é **Open-Meteo**, desde que os dados utilizados sejam adequados ao objetivo.

Coordenadas de Recife devem ser configuráveis.

Dados interessantes:

- precipitação;
- chuva;
- probabilidade de precipitação;
- temperatura;
- umidade;
- velocidade do vento;
- código meteorológico;
- timestamp.

Não consumir mais campos do que o necessário.

## Fonte 2 — Dados públicos do Recife

Investigar o **Portal de Dados Abertos da Prefeitura do Recife**, que utiliza CKAN.

Objetivo:

- localizar datasets reais relacionados a saúde, território, risco, equipamentos públicos ou outros dados úteis ao projeto;
- preferir acesso via API quando disponível;
- registrar URL, dataset, recurso e data de atualização.

## Fonte 3 — Saúde

Investigar uma fonte pública real de saúde.

Prioridade:

1. dados públicos da Prefeitura do Recife;
2. OpenDataSUS;
3. DATASUS;
4. outra fonte pública oficial.

Não inventar uma integração se a fonte for difícil.

Documentar o que foi encontrado e o que ainda depende de acesso.

---

# 6. Antes de programar integrações

Criar:

```text
docs/data-sources.md
```

Para cada fonte real, documentar:

```text
Nome:
Órgão responsável:
URL:
Tipo:
- API
- CSV
- Excel
- CKAN
- outro

Autenticação:
Frequência de atualização:
Campos utilizados:
Unidade territorial:
Limitações:
Licença:
Status:
- validada
- em análise
- indisponível
```

Só implementar um conector depois de validar que a fonte realmente existe e responde.

---

# 7. Estrutura inicial do repositório

Criar uma estrutura semelhante:

```text
nexoclima/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── domain/
│   │   ├── ingestion/
│   │   ├── transformation/
│   │   ├── classification/
│   │   ├── llm/
│   │   ├── mcp/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   ├── package.json
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── data-sources.md
│   ├── data-pipeline.md
│   ├── database-model.md
│   └── decisions/
│
├── scripts/
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

Não criar complexidade sem necessidade.

---

# 8. Variáveis de ambiente

Criar `.env.example`.

Nunca commitar credenciais.

Exemplo:

```env
# MongoDB Atlas
MONGODB_URI=
MONGODB_DATABASE=nexoclima_raw

# Neon
DATABASE_URL=

# External APIs
OPEN_METEO_BASE_URL=https://api.open-meteo.com

# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

# Future AI integration
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
```

Adicionar outras variáveis somente quando necessárias.

---

# 9. MongoDB Atlas — camada RAW

O Atlas deve armazenar o retorno original das APIs.

Não transformar o payload antes de guardar o RAW.

Criar coleção conceitual:

```text
raw_ingestions
```

Estrutura sugerida:

```json
{
  "source": "open_meteo",
  "endpoint": "...",
  "request_params": {},
  "collected_at": "...",
  "reference_period": {
    "start": "...",
    "end": "..."
  },
  "status": "success",
  "http_status": 200,
  "payload": {},
  "payload_hash": "...",
  "pipeline_version": "..."
}
```

Em erro:

```json
{
  "source": "...",
  "collected_at": "...",
  "status": "error",
  "http_status": 500,
  "error_type": "...",
  "error_message": "..."
}
```

Objetivos:

- auditoria;
- rastreabilidade;
- debug;
- reprocessamento;
- prova de que o sistema realmente consumiu a API.

---

# 10. Transformação — T

A transformação deve ser uma etapa explícita.

Não misturar coleta com transformação.

Fluxo:

```text
RAW
 ↓
VALIDAÇÃO
 ↓
NORMALIZAÇÃO
 ↓
PADRONIZAÇÃO
 ↓
CURATED
```

A transformação deve lidar com:

- timestamps;
- timezone;
- valores nulos;
- nomes de campos;
- tipos;
- unidades;
- territorialização;
- duplicidade;
- metadados;
- origem.

Criar modelos internos independentes do formato da fonte.

Exemplo conceitual:

```text
Measurement
- source
- indicator
- value
- unit
- reference_time
- collected_at
- latitude
- longitude
- territory_code
- metadata
```

A aplicação não deve depender diretamente do JSON do fornecedor externo.

---

# 11. Neon — camada CURATED

O Neon deve receber apenas dados já transformados.

Começar com um modelo relacional pequeno.

Tabelas iniciais sugeridas:

```text
data_sources
pipeline_runs
indicators
territories
measurements
classifications
```

## data_sources

Campos possíveis:

```text
id
name
provider
source_type
url
update_frequency
active
created_at
```

## pipeline_runs

```text
id
source_id
started_at
finished_at
status
raw_records
processed_records
error_records
error_message
```

## indicators

```text
id
code
name
category
unit
description
```

## territories

```text
id
code
name
type
latitude
longitude
geometry
```

## measurements

```text
id
source_id
indicator_id
territory_id
reference_time
collected_at
value
unit
raw_ingestion_id
created_at
```

## classifications

```text
id
measurement_id
classification_type
label
score
rule_version
classified_at
```

Criar migrações com Alembic.

---

# 12. Idempotência

O pipeline não deve inserir o mesmo dado indefinidamente.

Definir estratégia de deduplicação.

Possível chave lógica:

```text
source + indicator + territory + reference_time
```

A estratégia exata depende da fonte.

Documentar em:

```text
docs/data-pipeline.md
```

---

# 13. Pipeline

Criar o primeiro fluxo real:

```text
Open-Meteo
    ↓
HTTP request
    ↓
MongoDB Atlas RAW
    ↓
transform_weather()
    ↓
Neon PostgreSQL
    ↓
FastAPI
    ↓
Dashboard
```

Só depois de esse fluxo funcionar, adicionar segunda fonte.

---

# 14. Execução automática

A coleta não pode depender apenas de apertar um botão no dashboard.

Criar uma estratégia simples de agendamento.

Para POC pode ser:

- APScheduler;
- cron;
- job de plataforma;
- outra solução simples e documentada.

Não adicionar Airflow, Kafka ou ferramentas pesadas sem justificativa real.

Registrar toda execução em `pipeline_runs`.

---

# 15. Backend — endpoints iniciais

Criar endpoints reais, por exemplo:

```text
GET /health

GET /api/v1/sources

GET /api/v1/sources/status

GET /api/v1/indicators

GET /api/v1/measurements

GET /api/v1/measurements/latest

GET /api/v1/pipeline/runs

POST /api/v1/pipeline/run/{source}
```

O endpoint manual de execução pode existir para demonstração/admin, mas a atualização principal deve ser automatizável.

Implementar filtros quando necessário:

```text
source
indicator
start
end
territory
```

---

# 16. Dashboard

O dashboard só deve começar depois que o primeiro pipeline estiver persistindo dados reais no Neon.

Primeira versão:

## Card 1

Última coleta

Mostrar:

- fonte;
- horário;
- status.

## Card 2

Número de registros processados

## Gráfico

Série temporal de uma variável real.

Exemplo:

- precipitação;
- temperatura.

## Status das fontes

Tabela:

```text
Fonte
Última atualização
Status
Registros
```

## Mapa

Só adicionar se existir dado territorial/geográfico real.

Não inventar áreas de risco.

---

# 17. Classificação

A classificação deve ser implementada inicialmente por regras determinísticas.

Não começar usando LLM para classificar risco.

Exemplo conceitual:

```text
if precipitation >= threshold_critical:
    classification = "critico"
elif precipitation >= threshold_attention:
    classification = "atencao"
else:
    classification = "normal"
```

IMPORTANTE:

Os thresholds acima NÃO devem ser inventados para uso real.

Criar inicialmente uma estrutura configurável e marcar os limiares como:

```text
pending_domain_validation
```

Até o cliente/professor fornecer ou validar regras.

A arquitetura deve permitir:

```text
Rule-based classification
        ↓
LLM explanation
```

O LLM pode explicar a classificação, mas não deve criar silenciosamente a regra.

---

# 18. LLM

Implementar LLM somente após:

- API real funcionando;
- Atlas funcionando;
- transformação funcionando;
- Neon funcionando;
- dashboard com dado real funcionando.

Primeiros usos aceitáveis:

## Resumo situacional

Receber dados estruturados e gerar algo como:

```text
"Nas últimas X horas, a precipitação..."
```

## Explicação

Explicar por que uma observação recebeu determinada classificação.

## Perguntas sobre os dados

Exemplo:

```text
"Qual foi o maior valor de precipitação registrado hoje?"
```

O LLM NÃO deve consultar o banco diretamente sem controle.

Criar uma camada de ferramentas/queries autorizadas.

---

# 19. MCP

Criar MCP em fase posterior.

Objetivo:

permitir que um cliente compatível com MCP consulte o NexoClima através de ferramentas controladas.

Possíveis tools:

```text
get_latest_weather
get_source_status
get_measurements
get_classifications
get_pipeline_runs
get_summary_context
```

Exemplo conceitual:

```text
LLM
 ↓
MCP Client
 ↓
NexoClima MCP Server
 ↓
Serviços internos
 ↓
Neon
```

Não permitir SQL arbitrário via MCP.

As tools devem possuir:

- schemas claros;
- parâmetros validados;
- consultas controladas;
- limites de resultados.

---

# 20. Observabilidade

Desde o início registrar:

- início da coleta;
- fim da coleta;
- fonte;
- status;
- quantidade de registros;
- erros;
- tempo de execução.

Usar logging estruturado.

Não depender apenas de `print()`.

---

# 21. Tratamento de falhas

Se uma API falhar:

```text
API FAIL
   ↓
registrar pipeline_run como error
   ↓
guardar contexto do erro
   ↓
não apagar último dado válido
   ↓
expor status da fonte
```

O dashboard deve conseguir mostrar:

```text
Fonte indisponível
Último dado válido: <timestamp>
```

---

# 22. Testes

Fixtures sintéticas são permitidas SOMENTE nos testes automatizados.

Criar:

- testes de transformação;
- testes de validação;
- testes de deduplicação;
- testes de API;
- testes de falha de fonte.

Não usar a API externa real em todos os testes.

Nos testes de integração, quando necessário, utilizar responses gravadas ou mocks explicitamente marcados como teste.

Isso não viola a regra de “sem dados mockados” na aplicação.

---

# 23. Segurança

Nunca:

- expor chaves no frontend;
- commitar `.env`;
- registrar secrets em logs;
- retornar credenciais pela API.

Acesso ao Atlas e Neon apenas pelo backend.

---

# 24. Proveniência do dado

Todo dado exibido deve ser rastreável.

Sempre que possível, permitir saber:

```text
Qual fonte?
Quando foi coletado?
Qual período representa?
Qual transformação foi aplicada?
Qual versão do pipeline?
```

Esse é um requisito importante do projeto.

---

# 25. README principal

O README deve conter:

1. Problema;
2. Objetivo;
3. Arquitetura;
4. Fluxo:

```text
API → Atlas → Transformação → Neon → API interna → Dashboard
```

5. Como configurar;
6. Como rodar backend;
7. Como rodar frontend;
8. Como criar bancos;
9. Como executar pipeline;
10. Como adicionar uma nova fonte;
11. Variáveis de ambiente;
12. Limitações atuais;
13. Roadmap.

---

# 26. ADRs — Architecture Decision Records

Criar pasta:

```text
docs/decisions/
```

Criar pelo menos:

```text
001-use-mongodb-atlas-for-raw.md
002-use-neon-for-curated-postgres.md
003-use-connectors-per-source.md
004-use-rule-based-classification-first.md
005-use-mcp-after-core-pipeline.md
```

Cada ADR:

```text
Contexto
Decisão
Alternativas
Consequências
```

---

# 27. Primeira entrega que você deve produzir agora

Não tente implementar o projeto inteiro de uma vez.

Execute nesta ordem:

## ETAPA 1 — Inspeção

1. Verificar o repositório atual.
2. Identificar arquivos existentes.
3. Não sobrescrever trabalho existente sem necessidade.
4. Criar um relatório curto do estado atual.

## ETAPA 2 — Estrutura

Criar a estrutura mínima necessária.

## ETAPA 3 — Documentação

Criar:

```text
docs/architecture.md
docs/data-sources.md
docs/data-pipeline.md
docs/database-model.md
.env.example
```

## ETAPA 4 — Fonte real

Validar uma API meteorológica real.

Preferência inicial:

Open-Meteo.

Fazer uma chamada real e registrar quais campos serão utilizados.

## ETAPA 5 — Atlas

Implementar conexão ao MongoDB Atlas.

Criar ingestão RAW.

## ETAPA 6 — Transformação

Implementar transformação de meteorologia para o modelo interno.

## ETAPA 7 — Neon

Criar conexão ao Neon.

Criar migrações.

Persistir dados transformados.

## ETAPA 8 — API interna

Criar endpoint para consultar dados persistidos.

## ETAPA 9 — Dashboard mínimo

Criar uma tela que mostre dados meteorológicos reais provenientes do Neon.

## ETAPA 10 — Automação

Adicionar job de atualização.

---

# 28. Definition of Done da primeira vertical slice

A primeira fatia do sistema só está concluída quando:

- [ ] existe uma API externa real sendo consumida;
- [ ] a resposta é armazenada no MongoDB Atlas;
- [ ] existe transformação explícita;
- [ ] dados tratados são persistidos no Neon;
- [ ] uma API FastAPI consulta esses dados;
- [ ] o React consome essa API;
- [ ] existe pelo menos um gráfico com dados reais;
- [ ] existe indicação da fonte;
- [ ] existe horário da última coleta;
- [ ] existe registro do pipeline;
- [ ] nenhum dado mockado é usado no fluxo funcional;
- [ ] o README explica como reproduzir o processo.

---

# 29. Não fazer agora

Não implementar agora:

- arquitetura de microsserviços;
- Kubernetes;
- Kafka;
- Airflow;
- classificação por LLM sem regra validada;
- RAG complexo;
- chatbot completo;
- múltiplas APIs simultaneamente antes da primeira vertical slice;
- autenticação complexa sem necessidade;
- mapa fictício;
- alertas com limiares inventados.

Primeiro fazer UMA vertical real funcionar.

---

# 30. Roadmap depois da primeira vertical

Após concluir:

```text
Open-Meteo
→ Atlas
→ T
→ Neon
→ FastAPI
→ React
```

seguir:

## Fase 2

Adicionar segunda fonte real.

Preferência:

- dataset oficial da Prefeitura do Recife;
- fonte territorial.

## Fase 3

Adicionar fonte de saúde real.

## Fase 4

Integração por tempo e território.

## Fase 5

Classificação.

## Fase 6

Resumo com LLM.

## Fase 7

MCP.

---

# 31. O que eu quero de você, Claude Code, nesta primeira execução

1. Leia este arquivo inteiro.
2. Inspecione o repositório.
3. Produza um plano curto de execução baseado no que já existe.
4. Não altere tecnologias existentes sem justificar.
5. Identifique o menor caminho para a primeira vertical slice.
6. Crie ou ajuste a estrutura do projeto.
7. Implemente a configuração inicial do backend.
8. Implemente a primeira fonte de dados real.
9. Implemente as integrações com Atlas e Neon de forma configurável por `.env`.
10. Crie migrações.
11. Crie testes essenciais.
12. Atualize a documentação.
13. Não use dados mockados no fluxo funcional.
14. Se uma credencial for necessária, pare apenas naquele ponto específico, documente exatamente qual variável é necessária e continue tudo que puder sem ela.
15. Não invente credenciais, endpoints privados ou datasets inexistentes.

---

# 32. Informações que ainda dependem do usuário

Se necessário, solicitar apenas:

```text
MONGODB_URI
DATABASE_URL (Neon)
```

Posteriormente:

```text
LLM_API_KEY
```

Não exigir chave para a primeira API pública se uma fonte sem autenticação puder ser utilizada.

---

# 33. Perguntas que precisam ser validadas com o professor/cliente

Manter em documentação como pendências:

1. “Atlas” significa realmente MongoDB Atlas?
2. “T” representa transformação/ETL?
3. O professor espera MongoDB Atlas como RAW e Neon como CURATED?
4. Quais APIs/fontes são obrigatórias?
5. Existe fonte oficial específica que deve ser utilizada?
6. Quais indicadores devem ser classificados?
7. Quais regras/limiares definem classificação?
8. Qual papel esperado do LLM?
9. Qual papel esperado do MCP?
10. O MCP deve ser apenas demonstração técnica ou parte funcional do produto?

Essas dúvidas não devem bloquear a primeira vertical slice.

---

# 34. Resultado esperado da primeira POC

Ao final da primeira etapa deve ser possível demonstrar ao professor:

```text
1. Esta é a API real.

2. Estes são os dados retornados.

3. O payload bruto entrou no MongoDB Atlas.

4. Esta transformação foi aplicada.

5. Estes são os dados tratados no Neon.

6. Esta API interna consulta o Neon.

7. Este dashboard é alimentado pelos dados reais.

8. Esta é a última hora de coleta.

9. Este é o status do pipeline.

10. Se a fonte falhar, o sistema registra a falha.
```

A demonstração deve permitir acompanhar o dado de ponta a ponta.

---

# 35. Filosofia do projeto

A principal frase técnica do NexoClima é:

> **A principal automação acontece antes do dashboard.**

E a arquitetura deve refletir isso:

```text
Fonte real
   ↓
Ingestão
   ↓
Raw
   ↓
Transformação
   ↓
Curated
   ↓
Classificação
   ↓
Uso
   ↓
Decisão
```

Comece simples, mas real.

Uma fonte real completamente integrada vale mais para esta POC do que cinco telas alimentadas por dados fictícios.
