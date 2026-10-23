import { useState } from 'react';
import { useLatestMeasurements } from '../hooks/useLatestMeasurements';

export const LatestMeasurements = () => {
  const { data, loading, error } = useLatestMeasurements();
  const [isExpanded, setIsExpanded] = useState(false);

  if (loading) {
    return <div className="loading">Carregando medições...</div>;
  }

  if (error) {
    return <div className="error">Erro: {error}</div>;
  }

  // Filtrar apenas indicadores climáticos (excluir epidemiologia)
  // Lista de códigos de indicadores epidemiológicos para excluir
  const epidemiologyCodes = [
    'dengue_casos_est',
    'dengue_casos',
    'dengue_nivel_alerta',
    'chik_casos_est',
    'chik_casos',
    'chik_nivel_alerta',
    'zika_casos_est',
    'zika_casos',
    'zika_nivel_alerta',
    'temp_media_epi',
    'umidade_media_epi',
  ];

  const weatherData = data.filter((m) => {
    const code = m.indicator_code || '';
    return !epidemiologyCodes.includes(code);
  });

  if (weatherData.length === 0) {
    return (
      <div className="error">
        Nenhuma medição climática encontrada. Execute o pipeline primeiro.
      </div>
    );
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Ícones para cada tipo de indicador
  const getIcon = (code: string) => {
    if (code.includes('temp')) return '🌡️';
    if (code.includes('precip') || code.includes('rain')) return '🌧️';
    if (code.includes('humidity') || code.includes('umid')) return '💧';
    if (code.includes('wind')) return '💨';
    if (code.includes('weather')) return '☁️';
    return '📊';
  };

  return (
    <div className="collapsible-section">
      <button
        className={`collapsible-header ${isExpanded ? 'expanded' : ''}`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="header-content">
          <span className="header-icon">📋</span>
          <span className="header-title">Todas as Medições ({weatherData.length})</span>
        </div>
        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="collapsible-content">
          <div className="measurements-grid">
            {weatherData.map((measurement) => (
              <div key={measurement.id} className="measurement-item">
                <div className="measurement-icon">
                  {getIcon(measurement.indicator_code)}
                </div>
                <h3>{measurement.indicator_name}</h3>
                <div className="measurement-value">
                  {measurement.value.toFixed(1)} <span className="unit">{measurement.unit}</span>
                </div>
                <div className="measurement-time">
                  {formatDateTime(measurement.reference_time)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
