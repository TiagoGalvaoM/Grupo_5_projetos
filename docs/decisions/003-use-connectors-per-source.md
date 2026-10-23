# ADR 003: Um conector por fonte de dados

## Status
Aceito

## Contexto
O sistema precisa integrar múltiplas fontes externas heterogêneas (APIs REST, CKAN, CSV, etc.). Cada fonte tem:
- Formato de resposta diferente
- Autenticação diferente
- Frequência de atualização diferente
- Estrutura de dados diferente

## Decisão
Criar **um conector específico por fonte** no módulo `app/ingestion/`.

Padrão:
```
app/ingestion/
├── __init__.py
├── base.py  (Classe abstrata BaseConnector)
├── weather_connector.py  (Open-Meteo)
├── recife_open_data_connector.py  (futuro)
└── health_connector.py  (futuro)
```

## Alternativas Consideradas

### 1. Conector genérico único
**Prós**:
- Menos código

**Contras**:
- Dificulta lidar com particularidades de cada fonte
- Complexidade crescente com condicionais
- Dificulta manutenção

### 2. Conectores por fonte (escolhido)
**Prós**:
- Separação clara de responsabilidades
- Fácil adicionar nova fonte
- Mudança em uma fonte não afeta outras
- Testes isolados por fonte

**Contras**:
- Mais arquivos
- Possível duplicação de código auxiliar

## Consequências

### Positivas
- Código organizado e rastreável
- Facilita onboarding de novos desenvolvedores
- Permite diferentes estratégias de retry/error handling por fonte
- Facilita desabilitar uma fonte problemática sem afetar outras

### Negativas
- Necessário criar nova classe para cada fonte
- Código comum deve ser extraído para `BaseConnector`

## Notas de Implementação

### Classe base
```python
class BaseConnector(ABC):
    @abstractmethod
    async def fetch(self) -> dict:
        """Busca dados da fonte externa"""
        pass

    @abstractmethod
    async def save_raw(self, payload: dict) -> str:
        """Salva payload no MongoDB"""
        pass

    @abstractmethod
    def get_transformer(self):
        """Retorna transformador específico"""
        pass
```

### Conector específico
```python
class WeatherConnector(BaseConnector):
    def __init__(self, config: dict):
        self.base_url = config["base_url"]
        self.latitude = config["latitude"]
        self.longitude = config["longitude"]

    async def fetch(self) -> dict:
        # Lógica específica para Open-Meteo
        ...
```

## Relação com Transformação
Cada conector sabe qual transformador usar:
```python
connector.get_transformer() -> WeatherTransformer
```

## Revisão
Esta decisão será revisada quando houver 5+ fontes e padrões comuns claros emergirem.
