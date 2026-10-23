import { useSourcesStatus } from '../hooks/useSourcesStatus';

export const SourcesStatus = () => {
  const { data, loading, error } = useSourcesStatus();

  if (loading) {
    return <div className="loading">Carregando status...</div>;
  }

  if (error) {
    return <div className="error">Erro: {error}</div>;
  }

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'Nunca executado';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  const getStatusBadge = (status?: string) => {
    if (!status) return <span className="status-badge">N/A</span>;

    const className = `status-badge status-${status}`;
    return <span className={className}>{status}</span>;
  };

  const getSourceIcon = (name: string) => {
    if (name.toLowerCase().includes('meteo')) return '☁️';
    if (name.toLowerCase().includes('dengue') || name.toLowerCase().includes('info')) return '🦟';
    return '📡';
  };

  return (
    <table className="source-table">
      <thead>
        <tr>
          <th>Fonte</th>
          <th>Status</th>
          <th>Última Coleta</th>
          <th>Medições</th>
        </tr>
      </thead>
      <tbody>
        {data.map((source) => (
          <tr key={source.source_id}>
            <td>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.5rem' }}>{getSourceIcon(source.source_name)}</span>
                <div>
                  <strong>{source.source_name}</strong>
                  {!source.active && <span style={{ color: '#999' }}> (Inativa)</span>}
                </div>
              </div>
            </td>
            <td>{getStatusBadge(source.last_status)}</td>
            <td>{formatDateTime(source.last_run)}</td>
            <td>
              <strong style={{ color: '#646cff' }}>
                {source.total_measurements.toLocaleString('pt-BR')}
              </strong>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
