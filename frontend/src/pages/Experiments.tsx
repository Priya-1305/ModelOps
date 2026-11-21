import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Experiment } from '../types';
import { FlaskConical, RefreshCw, Layers } from 'lucide-react';

export const Experiments: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExperiments();
  }, []);

  const loadExperiments = async () => {
    try {
      setLoading(true);
      const res = await api.getExperiments();
      setExperiments(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Experiment Tracking</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            MLflow-synchronized experiments, runs, artifacts, and hyperparameter trials.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadExperiments}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {experiments.length === 0 ? (
        <div className="stat-card" style={{ textAlign: 'center', padding: '48px' }}>
          <FlaskConical size={40} color="var(--text-dim)" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>No Experiments Found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Trigger a training run to record runs under an MLflow experiment.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {experiments.map((exp) => (
            <div key={exp.id} className="stat-card" style={{ gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <FlaskConical size={20} color="var(--accent-purple)" />
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{exp.name}</h3>
                    <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>{exp.description || 'No description'}</p>
                  </div>
                </div>
                <span className="badge badge-staging">{exp.run_count} Runs Recorded</span>
              </div>

              {exp.runs && exp.runs.length > 0 && (
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Run</th>
                        <th>Model Architecture</th>
                        <th>Val F1</th>
                        <th>Val ROC-AUC</th>
                        <th>Test Accuracy</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {exp.runs.map((r) => (
                        <tr key={r.id}>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{r.run_name}</td>
                          <td>{r.model_type}</td>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.val_f1_score?.toFixed(4) || '-'}</td>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.val_roc_auc?.toFixed(4) || '-'}</td>
                          <td style={{ fontFamily: 'var(--font-mono)' }}>{r.metrics?.test_accuracy?.toFixed(4) || '-'}</td>
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
          ))}
        </div>
      )}
    </div>
  );
};
