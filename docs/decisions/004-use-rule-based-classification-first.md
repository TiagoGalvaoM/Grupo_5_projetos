# ADR 004: Classificação baseada em regras determinísticas primeiro

## Status
Aceito

## Contexto
O sistema precisa classificar situações de risco (ex: precipitação crítica, temperatura extrema). Há duas abordagens possíveis:
1. Regras determinísticas (if/then baseado em limiares)
2. Classificação via LLM

## Decisão
Implementar **classificação baseada em regras determinísticas** inicialmente, com possível explicação via LLM posteriormente.

## Alternativas Consideradas

### 1. Classificação direta via LLM
**Prós**:
- Flexível
- Pode considerar contexto complexo

**Contras**:
- Não determinístico
- Dificulta auditoria
- Custo por classificação
- Dependência de serviço externo
- Sistema não funciona sem LLM

### 2. Regras determinísticas (escolhido)
**Prós**:
- Determinístico e auditável
- Zero custo
- Rápido
- Sistema independente de LLM
- Regras podem ser validadas com cliente/especialista

**Contras**:
- Menos flexível
- Precisa de domínio especializado para definir limiares

## Consequências

### Positivas
- Sistema funciona sem dependência de LLM
- Regras claras e rastreáveis
- Performance previsível
- Fácil de testar
- Cliente pode validar/ajustar limiares

### Negativas
- Limiares precisam ser definidos com especialista
- Regras rígidas (menos adaptação a contexto)

## Arquitetura

```python
# Regra determinística
class RiskClassifier:
    def classify_precipitation(self, value: float) -> str:
        if value >= THRESHOLD_CRITICAL:  # A validar com cliente
            return "critico"
        elif value >= THRESHOLD_ATTENTION:
            return "atencao"
        return "normal"
```

```python
# LLM opcional para explicação
class LLMExplainer:
    def explain_classification(
        self,
        measurement: Measurement,
        classification: Classification
    ) -> str:
        # Gera explicação em linguagem natural
        # do porquê da classificação
        ...
```

## Fluxo

```
Measurement → Rule-based Classification → [opcional] LLM Explanation
```

**Importante**: LLM explica, não classifica.

## Notas de Implementação

### Fase 1
- Criar estrutura de regras configurável
- Marcar limiares como `pending_domain_validation`
- Documentar que valores são exemplos, não validados

### Fase 2
- Validar limiares com cliente/especialista
- Implementar regras validadas
- Adicionar versionamento de regras

### Fase 3 (Opcional)
- Adicionar LLM para explicação
- Manter regras como fonte primária

## Exemplo de Configuração

```yaml
risk_thresholds:
  precipitation:
    critical: 50  # mm/h - PENDING VALIDATION
    attention: 20  # mm/h - PENDING VALIDATION
    description: "Valores de exemplo, necessitam validação com Vigidesastres"
```

## Revisão
Esta decisão será revisada após validação de regras com o cliente e avaliação de necessidade de LLM.
