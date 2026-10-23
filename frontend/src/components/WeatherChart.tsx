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

interface WeatherChartProps {
  indicator: string;
}

export const WeatherChart = ({ indicator }: WeatherChartProps) => {
  const { data, loading, error } = useMeasurements({ indicator, limit: 50 });

  if (loading) {
    return <div className="loading">Carregando gráfico...</div>;
  }

  if (error) {
    return <div className="error">Erro ao carregar gráfico: {error}</div>;
  }

  if (data.length === 0) {
    return (
      <div className="error">
        Nenhum dado encontrado para o indicador "{indicator}". Execute o pipeline primeiro.
      </div>
    );
  }

  // Preparar dados para o gráfico
  const chartData = data
    .map((m) => ({
      time: new Date(m.reference_time).toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
      }),
      value: m.value,
      fullTime: m.reference_time,
    }))
    .reverse(); // Ordem cronológica

  const unit = data[0]?.unit || '';
  const indicatorName = data[0]?.indicator_name || indicator;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis
          dataKey="time"
          stroke="#999"
          style={{ fontSize: '0.75rem' }}
        />
        <YAxis
          stroke="#999"
          style={{ fontSize: '0.75rem' }}
          label={{ value: unit, angle: -90, position: 'insideLeft', fill: '#999' }}
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
          stroke="#646cff"
          strokeWidth={2}
          dot={{ fill: '#646cff', r: 4 }}
          activeDot={{ r: 6 }}
          name={indicatorName}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
