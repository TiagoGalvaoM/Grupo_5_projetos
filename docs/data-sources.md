# Fontes de Dados - NexoClima

## Fonte 1: Open-Meteo (Meteorologia)

**Nome**: Open-Meteo Weather API
**Órgão responsável**: Open-Meteo (Serviço público)
**URL**: https://api.open-meteo.com/v1/forecast
**Tipo**: API REST pública

**Autenticação**: Não requerida (uso não-comercial)
**Frequência de atualização**: Horária
**Unidade territorial**: Coordenadas geográficas (lat/lon)
**Coordenadas Recife**: -8.05, -34.9

**Campos utilizados**:
- `temperature_2m`: Temperatura a 2m (°C)
- `precipitation`: Precipitação acumulada (mm)
- `rain`: Chuva (mm)
- `precipitation_probability`: Probabilidade de precipitação (%)
- `relative_humidity_2m`: Umidade relativa (%)
- `wind_speed_10m`: Velocidade do vento a 10m (km/h)
- `weather_code`: Código meteorológico WMO
- `time`: Timestamp das observações

**Exemplo de Request**:
```
GET https://api.open-meteo.com/v1/forecast?latitude=-8.05&longitude=-34.9&hourly=temperature_2m,precipitation,rain,precipitation_probability,relative_humidity_2m,wind_speed_10m,weather_code&timezone=America/Recife
```

**Limitações**:
- Limite de 10.000 requests/dia (não-comercial)
- Dados de forecast, não observações reais de estações
- Cobertura limitada a previsões meteorológicas

**Licença**: Attribution 4.0 International (CC BY 4.0)
**Status**: ✅ Validada (Fonte primária para POC)

**Documentação**: https://open-meteo.com/en/docs

---

## Fonte 2: Portal de Dados Abertos do Recife (Em análise)

**Nome**: Portal de Dados Abertos da Prefeitura do Recife
**Órgão responsável**: Prefeitura do Recife
**URL**: http://dados.recife.pe.gov.br/
**Tipo**: CKAN

**Autenticação**: A investigar
**Frequência de atualização**: Varia por dataset
**Unidade territorial**: Bairros/Regionais de Recife

**Datasets de interesse** (a investigar):
- Equipamentos de saúde
- Dados territoriais
- Indicadores socioeconômicos
- Dados ambientais

**Status**: 🔍 Em análise
**Próximos passos**:
- Explorar catálogo de datasets
- Identificar API CKAN
- Validar formato de acesso
- Documentar campos disponíveis

---

## Fonte 3: OpenDataSUS / DATASUS (Planejada)

**Nome**: Dados públicos de saúde
**Órgão responsável**: Ministério da Saúde
**URL**: https://opendatasus.saude.gov.br/
**Tipo**: A investigar (API, CSV, arquivos)

**Status**: 📋 Planejada para Fase 3
**Objetivo**: Integrar indicadores de saúde pública
**Limitações**: Pode exigir download de arquivos bulk, não API em tempo real

---

## Fonte 4: CEMADEN (Futuro - Opcional)

**Nome**: Centro Nacional de Monitoramento e Alertas de Desastres Naturais
**Órgão responsável**: MCTI
**URL**: http://www.cemaden.gov.br/
**Tipo**: A investigar

**Status**: 💡 Opcional
**Justificativa**: Dados reais de estações pluviométricas, caso Open-Meteo seja insuficiente

---

## Critérios de Seleção de Fontes

1. **Disponibilidade pública**: Dados acessíveis sem credenciais especiais
2. **Atualização regular**: Fonte mantida e atualizada
3. **Relevância**: Dados úteis para vigilância em saúde/desastres
4. **Formato acessível**: API REST, CKAN, ou CSV bem documentado
5. **Licença permissiva**: Uso permitido em projeto acadêmico

---

## Processo de Validação de Nova Fonte

Antes de implementar conector:

1. ✅ Verificar que a fonte existe e responde
2. ✅ Documentar estrutura de dados retornados
3. ✅ Confirmar campos úteis ao projeto
4. ✅ Testar manualmente pelo menos 3 requisições
5. ✅ Registrar limitações (rate limit, autenticação, etc)
6. ✅ Atualizar este documento
7. ✅ Criar ADR se decisão arquitetural envolvida

---

## Template para Nova Fonte

```markdown
## Fonte X: [Nome]

**Nome**:
**Órgão responsável**:
**URL**:
**Tipo**: API | CSV | Excel | CKAN | Outro

**Autenticação**:
**Frequência de atualização**:
**Campos utilizados**:
- campo1: descrição
- campo2: descrição

**Unidade territorial**:
**Limitações**:
**Licença**:
**Status**: validada | em análise | indisponível

**Exemplo de Request**:
```

---

## Histórico

- **2024-10-23**: Criação do documento, validação Open-Meteo como fonte primária
