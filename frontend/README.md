# NexoClima Frontend

Dashboard React para visualização de dados climáticos e saúde do sistema NexoClima.

## Tecnologias

- React 18
- TypeScript
- Vite
- Recharts (gráficos)
- Axios (HTTP client)

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:5173

## Build

```bash
npm run build
```

## Funcionalidades

### Dashboard Principal

1. **Últimas Medições**
   - Card com últimas medições de cada indicador
   - Valores em tempo real da API

2. **Status das Fontes**
   - Tabela com status de cada fonte de dados
   - Última coleta
   - Total de medições

3. **Gráfico de Série Temporal**
   - Visualização de séries temporais
   - Seletor de indicador (Precipitação, Temperatura, Umidade, Vento)
   - Dados reais do backend

## Estrutura

```
src/
├── components/          # Componentes React
│   ├── Dashboard.tsx
│   ├── LatestMeasurements.tsx
│   ├── SourcesStatus.tsx
│   └── WeatherChart.tsx
├── hooks/              # Custom hooks
│   ├── useLatestMeasurements.ts
│   ├── useMeasurements.ts
│   └── useSourcesStatus.ts
├── services/           # API client
│   └── api.ts
├── types/              # TypeScript types
│   └── index.ts
├── App.tsx             # Componente raiz
└── main.tsx            # Entry point
```

## API Proxy

O Vite está configurado para fazer proxy das requisições `/api` para o backend em `http://localhost:8000`.

Isso permite fazer requisições como:
```typescript
axios.get('/api/v1/measurements/latest')
```

Que serão redirecionadas para:
```
http://localhost:8000/api/v1/measurements/latest
```

## Requisitos

- Backend rodando em http://localhost:8000
- Dados no banco (execute o pipeline primeiro)

## Troubleshooting

### Erro de CORS
- Verifique se backend está rodando
- CORS já está configurado no FastAPI

### Nenhum dado exibido
- Execute o pipeline do backend primeiro:
  ```bash
  cd backend
  poetry run python scripts/run_pipeline_manual.py
  ```

### Erro de conexão
- Verifique se backend está em http://localhost:8000
- Verifique proxy no `vite.config.ts`
