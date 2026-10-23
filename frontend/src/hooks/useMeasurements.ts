import { useState, useEffect } from 'react';
import { measurementsApi } from '../services/api';
import { Measurement } from '../types';

interface UseMeasurementsParams {
  indicator?: string;
  limit?: number;
}

export const useMeasurements = ({ indicator, limit = 100 }: UseMeasurementsParams = {}) => {
  const [data, setData] = useState<Measurement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const measurements = await measurementsApi.getAll({ indicator, limit });
        setData(measurements);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao buscar medições');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [indicator, limit]);

  return { data, loading, error };
};
