import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ModelSummary, SystemHealth, DriftReport, PredictionLog, TrainingRun } from '../types';
import { 
  Layers, 
  Activity, 
  Zap, 
  AlertTriangle, 
  CheckCircle2, 
  Database, 
  Clock, 
  Server,
  Play
} from 'lucide-react';

interface Props {
  onNavigate: (page: string) => void;
}

export const Overview: React.FC<Props> = ({ onNavigate }) => {
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [drift, setDrift] = useState<DriftReport | null>(null);
  const [logs, setLogs] = useState<PredictionLog[]>([]);
  const [runs, setRuns] = useState<TrainingRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [modelsData, healthData, driftData, logsData, runsData] = await Promise.allSettled([
        api.getModels(),
        api.getReadiness(),
        api.getDriftReport(),
        api.getPredictionLogs(),
        api.getTrainingRuns(),
      ]);

      if (modelsData.status === 'fulfilled') setModels(modelsData.value);
      if (healthData.status === 'fulfilled') setHealth(healthData.value);
      if (driftData.status === 'fulfilled') setDrift(driftData.value);
      if (logsData.status === 'fulfilled') setLogs(logsData.value);
      if (runsData.status === 'fulfilled') setRuns(runsData.value);
    } finally {
      setLoading(false);
    }
  };

  const avgLatency = logs.length > 0 
    ? (logs.reduce((acc, curr) => acc + curr.latency_ms, 0) / logs.length).toFixed(2)
    : '0.00';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.02em' }}>Platform Overview</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Production ML serving health, deployment status, and drift observability.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={loadDashboardData}>
            <Clock size={16} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => onNavigate('prediction-explorer')}>
            <Play size={16} /> Test Inference
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-4">
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Registered Models</span>
            <Layers size={18} color="var(--accent-blue)" />
          </div>
          <span className="stat-value">{models.length}</span>
          <span className="stat-sub">{models.reduce((acc, m) => acc + m.version_count, 0)} total versions</span>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Production Model</span>
            <CheckCircle2 size={18} color="var(--accent-emerald)" />
          </div>
          <span className="stat-value" style={{ fontSize: '1.25rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {health?.active_model || 'None'}
          </span>
          <span className="stat-sub">Active version: {health?.active_version ? `v${health.active_version}` : 'Not warmed'}</span>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Prediction Volume</span>
            <Zap size={18} color="var(--accent-cyan)" />
          </div>
          <span className="stat-value">{logs.length}</span>
          <span className="stat-sub">Avg latency: {avgLatency} ms</span>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-label">Drift Status</span>
            {drift?.data_drift_detected ? (
              <AlertTriangle size={18} color="var(--accent-amber)" />
            ) : (
              <CheckCircle2 size={18} color="var(--accent-emerald)" />
            )}
          </div>
          <span className="stat-value" style={{ color: drift?.data_drift_detected ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
            {drift?.data_drift_detected ? 'Drift Alert' : 'Normal'}
          </span>
          <span className="stat-sub">
            {drift ? `${drift.drifted_features_count}/${drift.total_features_count} drifted (${(drift.drift_share * 100).toFixed(0)}%)` : 'No report'}
          </span>
        </div>
      </div>

      {/* Quick Status / Recent Activity Grid */}
      <div className="grid-2">
        {/* Recent Training Runs */}
        <div className="stat-card" style={{ gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Recent Training Runs</h3>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onNavigate('training-runs')}>
              View All
            </button>
          </div>
          {runs.length === 0 ? (
            <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '24px' }}>No training runs recorded yet.</div>
          ) : (
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Run Name</th>
                    <th>Model Type</th>
                    <th>Val F1</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.slice(0, 5).map((r) => (
                    <tr key={r.id}>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{r.run_name}</td>
                      <td>{r.model_type}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>
                        {r.metrics?.val_f1_score ? r.metrics.val_f1_score.toFixed(4) : '-'}
                      </td>
                      <td>
                        <span className="badge badge-prod">{r.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recent Prediction Logs */}
        <div className="stat-card" style={{ gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Live Prediction Feed</h3>
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={() => onNavigate('prediction-explorer')}>
              Open Explorer
            </button>
          </div>
          {logs.length === 0 ? (
            <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '24px' }}>
              No prediction requests recorded yet. Trigger one via the Prediction Explorer.
            </div>
          ) : (
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Correlation ID</th>
                    <th>Prediction</th>
                    <th>Confidence</th>
                    <th>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.slice(0, 5).map((log) => {
                    const topProb = Math.max(...Object.values(log.probabilities || {}));
                    return (
                      <tr key={log.id}>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{log.correlation_id.slice(0, 8)}...</td>
                        <td>
                          <span className={`badge ${log.prediction === 1 ? 'badge-prod' : 'badge-candidate'}`}>
                            {log.prediction_label}
                          </span>
                        </td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{(topProb * 100).toFixed(1)}%</td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{log.latency_ms.toFixed(1)}ms</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
