import { useState } from 'react';
import { useMeasurements } from '../hooks/useMeasurements';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

type DiseaseType = 'dengue' | 'chikungunya' | 'zika';
type MetricType = 'casos_est' | 'casos' | 'nivel_alerta';

const DISEASES = {
  dengue: { name: 'Dengue', color: '#ff6b6b' },
  chikungunya: { name: 'Chikungunya', color: '#ffd93d' },
  zika: { name: 'Zika', color: '#6bcf7f' },
};

const METRICS = {
  casos_est: { name: 'Casos Estimados', unit: 'casos' },
  casos: { name: 'Casos Notificados', unit: 'casos' },
  nivel_alerta: { name: 'Nível de Alerta', unit: 'nível' },
};

const ALERT_LEVELS = {
  1: { color: '#4caf50', label: 'Verde - Normal' },
  2: { color: '#ffd93d', label: 'Amarelo - Atenção' },
  3: { color: '#ff9800', label: 'Laranja - Alerta' },
  4: { color: '#f44336', label: 'Vermelho - Crítico' },
};

export const EpidemiologyDashboard = () => {
  const [selectedDisease, setSelectedDisease] = useState<DiseaseType>('dengue');
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('casos_est');

  // Construir código do indicador: dengue_casos_est, chik_casos_est, etc
  const getIndicatorCode = (disease: DiseaseType, metric: MetricType) => {
    const diseasePrefix = disease === 'chikungunya' ? 'chik' : disease;
    return `${diseasePrefix}_${metric}`;
  };

  const indicatorCode = getIndicatorCode(selectedDisease, selectedMetric);
  const { data, loading, error } = useMeasurements({ indicator: indicatorCode, limit: 50 });

  // Últimas medições de cada doença (casos estimados)
  const dengueLatest = useMeasurements({ indicator: 'dengue_casos_est', limit: 1 });
  const chikLatest = useMeasurements({ indicator: 'chik_casos_est', limit: 1 });
  const zikaLatest = useMeasurements({ indicator: 'zika_casos_est', limit: 1 });

  // Níveis de alerta atuais
  const dengueAlertData = useMeasurements({ indicator: 'dengue_nivel_alerta', limit: 1 });
  const chikAlertData = useMeasurements({ indicator: 'chik_nivel_alerta', limit: 1 });
  const zikaAlertData = useMeasurements({ indicator: 'zika_nivel_alerta', limit: 1 });

  const getAlertLevel = (alertData: any) => {
    if (alertData.loading || !alertData.data || alertData.data.length === 0) return null;
    const level = Math.round(alertData.data[0].value);
    return ALERT_LEVELS[level as keyof typeof ALERT_LEVELS] || ALERT_LEVELS[1];
  };

  const dengueAlert = getAlertLevel(dengueAlertData);
  const chikAlert = getAlertLevel(chikAlertData);
  const zikaAlert = getAlertLevel(zikaAlertData);

  // Preparar dados para o gráfico
  const chartData =
    data && data.length > 0
      ? data
          .map((m) => {
            // Usar data completa ao invés de semana epidemiológica
            const date = new Date(m.reference_time);
            const displayDate = date.toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              year: '2-digit',
            });

            return {
              time: displayDate,
              value: m.value,
              fullTime: m.reference_time,
            };
          })
          .reverse() // Ordem cronológica
      : [];

  return (
    <div className="dashboard-grid">
      {/* Cards de Resumo - Última Semana Epidemiológica */}
      <section className="card">
        <h2>📊 Última Semana Epidemiológica</h2>
        <div className="disease-summary">
          <div className="disease-card">
            <h3>🦟 Dengue</h3>
            {dengueLatest.loading ? (
              <p>Carregando...</p>
            ) : dengueLatest.data && dengueLatest.data.length > 0 ? (
              <>
                <p className="cases-number">
                  {Math.round(dengueLatest.data[0].value)} casos est.
                </p>
                <p className="epiweek">
                  SE {dengueLatest.data[0].metadata?.epiweek || 'N/A'}
                </p>
              </>
            ) : (
              <p className="no-data">Sem dados</p>
            )}
          </div>

          <div className="disease-card">
            <h3>🦟 Chikungunya</h3>
            {chikLatest.loading ? (
              <p>Carregando...</p>
            ) : chikLatest.data && chikLatest.data.length > 0 ? (
              <>
                <p className="cases-number">
                  {Math.round(chikLatest.data[0].value)} casos est.
                </p>
                <p className="epiweek">
                  SE {chikLatest.data[0].metadata?.epiweek || 'N/A'}
                </p>
              </>
            ) : (
              <p className="no-data">Sem dados</p>
            )}
          </div>

          <div className="disease-card">
            <h3>🦟 Zika</h3>
            {zikaLatest.loading ? (
              <p>Carregando...</p>
            ) : zikaLatest.data && zikaLatest.data.length > 0 ? (
              <>
                <p className="cases-number">
                  {Math.round(zikaLatest.data[0].value)} casos est.
                </p>
                <p className="epiweek">SE {zikaLatest.data[0].metadata?.epiweek || 'N/A'}</p>
              </>
            ) : (
              <p className="no-data">Sem dados</p>
            )}
          </div>
        </div>
      </section>

      {/* Níveis de Alerta */}
      <section className="card">
        <h2>🚨 Níveis de Alerta</h2>
        <div className="alert-levels">
          <div className="alert-item">
            <span className="disease-label">Dengue:</span>
            {dengueAlert ? (
              <span
                className="alert-badge"
                style={{ backgroundColor: dengueAlert.color }}
              >
                {dengueAlert.label}
              </span>
            ) : (
              <span className="alert-badge" style={{ backgroundColor: '#666' }}>
                Carregando...
              </span>
            )}
          </div>

          <div className="alert-item">
            <span className="disease-label">Chikungunya:</span>
            {chikAlert ? (
              <span
                className="alert-badge"
                style={{ backgroundColor: chikAlert.color }}
              >
                {chikAlert.label}
              </span>
            ) : (
              <span className="alert-badge" style={{ backgroundColor: '#666' }}>
                Carregando...
              </span>
            )}
          </div>

          <div className="alert-item">
            <span className="disease-label">Zika:</span>
            {zikaAlert ? (
              <span
                className="alert-badge"
                style={{ backgroundColor: zikaAlert.color }}
              >
                {zikaAlert.label}
              </span>
            ) : (
              <span className="alert-badge" style={{ backgroundColor: '#666' }}>
                Carregando...
              </span>
            )}
          </div>
        </div>
      </section>

      {/* Gráfico de Série Temporal */}
      <section className="card chart-card">
        <div className="chart-header">
          <h2>📈 Série Temporal - Dados Epidemiológicos</h2>
          <div className="indicator-selectors">
            <div className="selector-group">
              <label htmlFor="disease">Doença:</label>
              <select
                id="disease"
                value={selectedDisease}
                onChange={(e) => setSelectedDisease(e.target.value as DiseaseType)}
              >
                {Object.entries(DISEASES).map(([key, { name }]) => (
                  <option key={key} value={key}>
                    {name}
                  </option>
                ))}
              </select>
            </div>

            <div className="selector-group">
              <label htmlFor="metric">Métrica:</label>
              <select
                id="metric"
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
              >
                {Object.entries(METRICS).map(([key, { name }]) => (
                  <option key={key} value={key}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="loading">Carregando gráfico...</div>
        ) : error ? (
          <div className="error">Erro ao carregar gráfico: {error}</div>
        ) : chartData.length === 0 ? (
          <div className="error">
            Nenhum dado encontrado para {DISEASES[selectedDisease].name} -{' '}
            {METRICS[selectedMetric].name}. Execute o pipeline InfoDengue primeiro.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="time"
                stroke="#999"
                style={{ fontSize: '0.75rem' }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis
                stroke="#999"
                style={{ fontSize: '0.75rem' }}
                label={{
                  value: METRICS[selectedMetric].unit,
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#999',
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #444',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#ccc' }}
              />
              <Legend wrapperStyle={{ color: '#ccc' }} />
              <Line
                type="monotone"
                dataKey="value"
                stroke={DISEASES[selectedDisease].color}
                strokeWidth={2}
                dot={{ fill: DISEASES[selectedDisease].color, r: 4 }}
                activeDot={{ r: 6 }}
                name={`${DISEASES[selectedDisease].name} - ${METRICS[selectedMetric].name}`}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
};
