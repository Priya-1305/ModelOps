export interface ModelVersion {
  id: string;
  model_name: string;
  version: string;
  stage: 'candidate' | 'staging' | 'production' | 'archived' | 'rejected' | string;
  metrics: {
    val_accuracy?: number;
    val_f1_score?: number;
    val_roc_auc?: number;
    test_accuracy?: number;
    test_f1_score?: number;
    test_roc_auc?: number;
    [key: string]: any;
  };
  parameters?: Record<string, any>;
  artifact_uri: string;
  training_run_id?: string;
  description?: string;
  created_at: string;
  promoted_at?: string;
}

export interface ModelSummary {
  id: string;
  name: string;
  description?: string;
  active_version?: string;
  version_count: number;
  created_at: string;
  updated_at: string;
}

export interface ModelDetail extends ModelSummary {
  versions: ModelVersion[];
}

export interface TrainingRun {
  id: string;
  run_name: string;
  experiment_id: string;
  status: string;
  model_type: string;
  version?: string;
  parameters: Record<string, any>;
  metrics: Record<string, any>;
  dataset_metadata: Record<string, any>;
  artifact_uri?: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
}

export interface Experiment {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  run_count: number;
  runs: TrainingRun[];
}

export interface PredictionResponse {
  prediction: number;
  prediction_label: string;
  probabilities: Record<string, number>;
  model_name: string;
  model_version: string;
  latency_ms: number;
  correlation_id: string;
  timestamp: string;
}

export interface PredictionLog {
  id: string;
  correlation_id: string;
  model_name: string;
  model_version: string;
  prediction: number;
  prediction_label: string;
  probabilities: Record<string, number>;
  latency_ms: number;
  features?: Record<string, any>;
  timestamp: string;
}

export interface FeatureDriftDetail {
  feature_name: string;
  drift_detected: boolean;
  drift_score: number;
  stat_test: string;
  threshold: number;
}

export interface DriftReport {
  id: string;
  model_name: string;
  model_version: string;
  generated_at: string;
  data_drift_detected: boolean;
  prediction_drift_detected: boolean;
  performance_degradation_detected?: boolean;
  drifted_features_count: number;
  total_features_count: number;
  drift_share: number;
  feature_details: FeatureDriftDetail[];
  summary: Record<string, any>;
  html_report_path?: string;
}

export interface SystemHealth {
  status: string;
  ready?: boolean;
  service?: string;
  environment?: string;
  uptime_seconds?: number;
  active_model?: string;
  active_version?: string;
}
