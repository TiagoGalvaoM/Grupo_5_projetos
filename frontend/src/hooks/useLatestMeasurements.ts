import { useState, useEffect } from 'react';
import { measurementsApi } from '../services/api';
import { Measurement } from '../types';

export const useLatestMeasurements = (territoryCode?: string) => {
  const [data, setData] = useState<Measurement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const measurements = await measurementsApi.getLatest(territoryCode);
        setData(measurements);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao buscar dados');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [territoryCode]);

  return { data, loading, error };
};
