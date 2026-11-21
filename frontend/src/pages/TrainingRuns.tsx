import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { TrainingRun } from '../types';
import { Play, RefreshCw, CheckCircle, Clock, Cpu } from 'lucide-react';

export const TrainingRuns: React.FC = () => {
  const [runs, setRuns] = useState<TrainingRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [modelType, setModelType] = useState<'logistic_regression' | 'random_forest'>('random_forest');
  const [nEstimators, setNEstimators] = useState(50);
  const [maxDepth, setMaxDepth] = useState(5);
  const [cParam, setCParam] = useState(1.0);
  const [triggering, setTriggering] = useState(false);
  const [selectedRun, setSelectedRun] = useState<TrainingRun | null>(null);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const res = await api.getTrainingRuns();
      setRuns(res);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerRun = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setTriggering(true);
      const hyperparameters =
        modelType === 'random_forest'
          ? { n_estimators: nEstimators, max_depth: maxDepth, random_state: 42 }
          : { C: cParam, max_iter: 500, random_state: 42 };

      await api.createTrainingRun({
        model_name: 'breast_cancer_classifier',
        model_type: modelType,
        hyperparameters,
        auto_register: true,
      });

      await loadRuns();
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Training Pipeline</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Reproducible dataset ingestion, preprocessing pipelines, model training, and MLflow tracking.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadRuns}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {/* Trigger Run Card */}
      <div className="stat-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={18} color="var(--accent-blue)" /> Trigger Training Run
        </h3>
        <form onSubmit={handleTriggerRun} style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              Model Architecture
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value as any)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
              }}
            >
              <option value="random_forest">Random Forest Classifier</option>
              <option value="logistic_regression">Logistic Regression (Baseline)</option>
            </select>
          </div>

          {modelType === 'random_forest' ? (
            <>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  n_estimators
                </label>
                <input
                  type="number"
                  value={nEstimators}
                  onChange={(e) => setNEstimators(parseInt(e.target.value) || 10)}
                  style={{
                    width: '100px',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  max_depth
                </label>
                <input
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(parseInt(e.target.value) || 2)}
                  style={{
                    width: '100px',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                  }}
                />
              </div>
            </>
          ) : (
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                C (Regularization)
              </label>
              <input
                type="number"
                step="0.1"
                value={cParam}
                onChange={(e) => setCParam(parseFloat(e.target.value) || 1.0)}
                style={{
                  width: '100px',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-main)',
                }}
              />
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={triggering}>
            <Play size={16} /> {triggering ? 'Executing Pipeline...' : 'Train Candidate'}
          </button>
        </form>
      </div>

      {/* Runs History Table */}
      <div className="stat-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Executed Runs</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Run Name</th>
                <th>Type</th>
                <th>Val Acc</th>
                <th>Val F1</th>
                <th>Val ROC-AUC</th>
                <th>Duration</th>
                <th>Date</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.run_name}</td>
                  <td>{r.model_type}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.val_accuracy?.toFixed(4) || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.val_f1_score?.toFixed(4) || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.val_roc_auc?.toFixed(4) || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{r.duration_seconds ? `${r.duration_seconds}s` : '-'}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(r.started_at).toLocaleString()}</td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                      onClick={() => setSelectedRun(r)}
                    >
                      Metrics
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedRun && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="stat-card" style={{ width: '650px', maxWidth: '90%', maxHeight: '85vh', overflowY: 'auto', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Run: {selectedRun.run_name}</h3>
              <button className="btn btn-secondary" onClick={() => setSelectedRun(null)}>Close</button>
            </div>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Hyperparameters</h4>
              <pre style={{ backgroundColor: 'var(--bg-main)', padding: '12px', borderRadius: '6px', fontSize: '0.8rem' }}>
                {JSON.stringify(selectedRun.parameters, null, 2)}
              </pre>
            </div>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Metrics & Confusion Matrix</h4>
              <pre style={{ backgroundColor: 'var(--bg-main)', padding: '12px', borderRadius: '6px', fontSize: '0.8rem' }}>
                {JSON.stringify(selectedRun.metrics, null, 2)}
              </pre>
            </div>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Dataset Metadata</h4>
              <pre style={{ backgroundColor: 'var(--bg-main)', padding: '12px', borderRadius: '6px', fontSize: '0.8rem' }}>
                {JSON.stringify(selectedRun.dataset_metadata, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
