import React, { useState } from 'react';
import { api } from '../services/api';
import { Activity, ExternalLink, RefreshCw, Play, AlertCircle, CheckCircle } from 'lucide-react';

export const Monitoring: React.FC = () => {
  const [retrainingReason, setRetrainingReason] = useState('Feature drift detected on 8 columns');
  const [retrainingModel, setRetrainingModel] = useState<'random_forest' | 'logistic_regression'>('random_forest');
  const [retrainingStatus, setRetrainingStatus] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRetrain = async () => {
    try {
      setLoading(true);
      const res = await api.triggerRetraining({
        reason: retrainingReason,
        model_type: retrainingModel,
      });
      setRetrainingStatus(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Observability & Monitoring</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Prometheus metric collection, Grafana dashboard integration, and retraining triggers.
          </p>
        </div>
        <a
          href="http://localhost:3001"
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          <ExternalLink size={16} /> Open Grafana Dashboard
        </a>
      </div>

      <div className="grid-3">
        <div className="stat-card">
          <span className="stat-label">Metrics Endpoint</span>
          <span className="stat-value" style={{ fontSize: '1rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
            /metrics
          </span>
          <span className="stat-sub">Scraped every 5s by Prometheus</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Prometheus Server</span>
          <span className="stat-value" style={{ fontSize: '1rem', fontFamily: 'var(--font-mono)' }}>
            localhost:9090
          </span>
          <span className="stat-sub">Scraping modelops-backend</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Grafana Provisioning</span>
          <span className="stat-value" style={{ fontSize: '1rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)' }}>
            Provisioned
          </span>
          <span className="stat-sub">ModelOps Dashboard Auto-Loaded</span>
        </div>
      </div>

      {/* Controlled Retraining Workflow Trigger */}
      <div className="stat-card" style={{ gap: '16px' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Controlled Automated Retraining Workflow</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          When data drift or performance decay is observed, trigger a candidate retraining run.
          The candidate is evaluated against production acceptance criteria before promotion approval.
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: '240px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
              Retraining Trigger Reason
            </label>
            <input
              type="text"
              value={retrainingReason}
              onChange={(e) => setRetrainingReason(e.target.value)}
              style={{
                width: '100%',
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
              Candidate Architecture
            </label>
            <select
              value={retrainingModel}
              onChange={(e) => setRetrainingModel(e.target.value as any)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
              }}
            >
              <option value="random_forest">Random Forest</option>
              <option value="logistic_regression">Logistic Regression</option>
            </select>
          </div>

          <button className="btn btn-primary" onClick={handleRetrain} disabled={loading}>
            <Play size={16} /> {loading ? 'Evaluating Candidate...' : 'Execute Retraining Pipeline'}
          </button>
        </div>

        {retrainingStatus && (
          <div style={{
            marginTop: '16px',
            padding: '16px',
            borderRadius: '6px',
            backgroundColor: retrainingStatus.recommendation === 'RECOMMENDED_FOR_PROMOTION' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
            border: `1px solid ${retrainingStatus.recommendation === 'RECOMMENDED_FOR_PROMOTION' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 700, color: retrainingStatus.recommendation === 'RECOMMENDED_FOR_PROMOTION' ? '#34d399' : '#fb7185' }}>
                Recommendation: {retrainingStatus.recommendation}
              </span>
              <span className="badge badge-candidate">Candidate: v{retrainingStatus.candidate_version}</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>{retrainingStatus.decision_rationale}</p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              F1 Delta: {retrainingStatus.metric_deltas.delta_f1_score > 0 ? '+' : ''}{retrainingStatus.metric_deltas.delta_f1_score} | 
              ROC-AUC Delta: {retrainingStatus.metric_deltas.delta_roc_auc > 0 ? '+' : ''}{retrainingStatus.metric_deltas.delta_roc_auc}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginTop: '4px' }}>
              {retrainingStatus.promotion_instructions}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
