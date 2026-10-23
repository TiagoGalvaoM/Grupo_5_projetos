import { useState, useEffect } from 'react';
import { sourcesApi } from '../services/api';
import { SourceStatus } from '../types';

export const useSourcesStatus = () => {
  const [data, setData] = useState<SourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const sources = await sourcesApi.getStatus();
        setData(sources);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao buscar status das fontes');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
};
