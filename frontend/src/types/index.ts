export interface Measurement {
  id: number;
  value: number;
  unit: string;
  reference_time: string;
  collected_at: string;
  source_name: string;
  indicator_code: string;
  indicator_name: string;
  territory_name?: string;
}

export interface SourceStatus {
  source_id: number;
  source_name: string;
  active: boolean;
  last_run?: string;
  last_status?: string;
  total_measurements: number;
}

export interface PipelineRun {
  id: string;
  source_id: number;
  started_at: string;
  finished_at?: string;
  status: 'running' | 'success' | 'error';
  raw_records: number;
  processed_records: number;
  error_records: number;
  error_message?: string;
  duration_seconds?: number;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  postgres?: string;
  mongodb?: string;
  error?: string;
}
