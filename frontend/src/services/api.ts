import {
  ModelSummary,
  ModelDetail,
  ModelVersion,
  TrainingRun,
  Experiment,
  PredictionResponse,
  PredictionLog,
  DriftReport,
  SystemHealth,
} from '../types';

const API_BASE = '/api/v1';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errObj = await res.json();
      if (errObj.error?.message) {
        errorDetail = errObj.error.message;
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJSON<SystemHealth>('/health'),
  getReadiness: () => fetchJSON<SystemHealth>('/ready'),

  // Models & Registry
  getModels: () => fetchJSON<ModelSummary[]>('/models'),
  getModelDetails: (id: string) => fetchJSON<ModelDetail>(`/models/${id}`),
  getModelVersions: (id: string) => fetchJSON<ModelVersion[]>(`/models/${id}/versions`),
  promoteModel: (id: string, version: string, data: { minimum_f1_score?: number; minimum_roc_auc?: number; force?: boolean; comment?: string }) =>
    fetchJSON<ModelVersion>(`/models/${id}/versions/${version}/promote`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  rollbackModel: (id: string, data: { target_version?: string; comment?: string }) =>
    fetchJSON<ModelVersion>(`/models/${id}/rollback`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Training & Experiments
  getTrainingRuns: () => fetchJSON<TrainingRun[]>('/training-runs'),
  getTrainingRun: (id: string) => fetchJSON<TrainingRun>(`/training-runs/${id}`),
  createTrainingRun: (data: { model_name: string; model_type: string; hyperparameters?: Record<string, any>; auto_register?: boolean }) =>
    fetchJSON<TrainingRun>('/training-runs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getExperiments: () => fetchJSON<Experiment[]>('/experiments'),

  // Predictions
  predict: (features: Record<string, number>, model_version?: string) =>
    fetchJSON<PredictionResponse>('/predictions', {
      method: 'POST',
      body: JSON.stringify({ features, model_version }),
    }),
  getPredictionLogs: () => fetchJSON<PredictionLog[]>('/predictions'),

  // Monitoring & Drift
  getDriftReport: () => fetchJSON<DriftReport>('/monitoring/drift'),
  runDriftCheck: () => fetchJSON<DriftReport>('/monitoring/drift/run', { method: 'POST' }),

  // Retraining
  triggerRetraining: (data: { reason: string; model_type: string; hyperparameters?: Record<string, any> }) =>
    fetchJSON<any>('/retraining/trigger', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
