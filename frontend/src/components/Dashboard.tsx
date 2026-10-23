import { useState } from 'react';
import { LatestMeasurements } from './LatestMeasurements';
import { SourcesStatus } from './SourcesStatus';
import { WeatherChart } from './WeatherChart';
import { EpidemiologyDashboard } from './EpidemiologyDashboard';
import './Dashboard.css';

type TabType = 'weather' | 'epidemiology';

export const Dashboard = () => {
  const [activeTab, setActiveTab] = useState<TabType>('weather');
  const [selectedIndicator, setSelectedIndicator] = useState<string>('precipitation');

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>NexoClima Dashboard</h1>
        <p className="subtitle">
          Vigilância em Saúde / Vigidesastres - Secretaria de Saúde do Recife
        </p>

        {/* Navegação por Abas */}
        <nav className="tabs">
          <button
            className={`tab ${activeTab === 'weather' ? 'active' : ''}`}
            onClick={() => setActiveTab('weather')}
          >
            ☁️ Dados Climáticos
          </button>
          <button
            className={`tab ${activeTab === 'epidemiology' ? 'active' : ''}`}
            onClick={() => setActiveTab('epidemiology')}
          >
            🦟 Dados Epidemiológicos
          </button>
        </nav>
      </header>

      {/* Conteúdo baseado na aba ativa */}
      {activeTab === 'weather' ? (
        <div className="dashboard-grid">
          {/* Última Coleta - Clima */}
          <section className="card">
            <h2>Últimas Medições - Clima</h2>
            <LatestMeasurements />
          </section>

          {/* Status das Fontes */}
          <section className="card">
            <h2>Status das Fontes</h2>
            <SourcesStatus />
          </section>

          {/* Gráfico de Série Temporal - Clima */}
          <section className="card chart-card">
            <div className="chart-header">
              <h2>Série Temporal - Indicadores Climáticos</h2>
              <div className="indicator-selector">
                <label htmlFor="indicator">Indicador:</label>
                <select
                  id="indicator"
                  value={selectedIndicator}
                  onChange={(e) => setSelectedIndicator(e.target.value)}
                >
                  <option value="precipitation">💧 Precipitação</option>
                  <option value="temp_2m">🌡️ Temperatura</option>
                  <option value="humidity">💨 Umidade</option>
                  <option value="wind_speed">🌪️ Vento</option>
                </select>
              </div>
            </div>
            <WeatherChart indicator={selectedIndicator} />
          </section>
        </div>
      ) : (
        <EpidemiologyDashboard />
      )}

      <footer className="dashboard-footer">
        <p>
          ✅ Dados reais: Open-Meteo (clima) + InfoDengue (epidemiologia) |
          Rastreabilidade completa RAW → CURATED
        </p>
      </footer>
    </div>
  );
};
