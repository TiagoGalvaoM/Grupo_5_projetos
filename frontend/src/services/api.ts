import axios from 'axios';
import { Measurement, SourceStatus, PipelineRun, HealthStatus } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

export const healthApi = {
  check: async (): Promise<HealthStatus> => {
    const response = await axios.get<HealthStatus>('/health');
    return response.data;
  },
};

export const measurementsApi = {
  getLatest: async (territoryCode?: string): Promise<Measurement[]> => {
    const response = await api.get<Measurement[]>('/measurements/latest', {
      params: { territory_code: territoryCode },
    });
    return response.data;
  },

  getAll: async (params?: {
    source?: string;
    indicator?: string;
    start?: string;
    end?: string;
    limit?: number;
  }): Promise<Measurement[]> => {
    const response = await api.get<Measurement[]>('/measurements', { params });
    return response.data;
  },
};

export const sourcesApi = {
  getStatus: async (): Promise<SourceStatus[]> => {
    const response = await api.get<SourceStatus[]>('/sources/status');
    return response.data;
  },
};

export const pipelineApi = {
  getRuns: async (source?: string, limit?: number): Promise<PipelineRun[]> => {
    const response = await api.get<PipelineRun[]>('/pipeline/runs', {
      params: { source, limit },
    });
    return response.data;
  },
};
