import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DriftReport } from '../types';
import { AlertTriangle, CheckCircle2, RefreshCw, Info, FileText } from 'lucide-react';

export const DriftReports: React.FC = () => {
  const [report, setReport] = useState<DriftReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const res = await api.getDriftReport();
      setReport(res);
    } finally {
      setLoading(false);
    }
  };

  const handleRunCheck = async () => {
    try {
      setRunning(true);
      const res = await api.runDriftCheck();
      setReport(res);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Data & Feature Drift Reports</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Evidently-powered statistical distribution testing across all 30 input features.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={loadReport}>
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={handleRunCheck} disabled={running}>
            <AlertTriangle size={16} /> {running ? 'Analyzing Drift...' : 'Run Statistical Drift Check'}
          </button>
        </div>
      </div>

      {/* Methodological Guidance Banner */}
      <div style={{
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: 'rgba(59, 130, 246, 0.08)',
        border: '1px solid rgba(59, 130, 246, 0.25)',
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-start'
      }}>
        <Info size={20} color="var(--accent-blue)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
          <strong>Critical ML Engineering Distinction:</strong> Input feature drift (covariate shift) indicates that inference
          request distributions have changed relative to the baseline training split. <em>Feature drift alone does NOT prove model accuracy degradation</em>,
          as the underlying decision boundaries or conditional label probabilities may remain invariant. Verification requires ground truth labels.
        </div>
      </div>

      {/* Drift KPI Summary */}
      <div className="grid-4">
        <div className="stat-card">
          <span className="stat-label">Overall Status</span>
          <span className="stat-value" style={{ color: report?.data_drift_detected ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
            {report?.data_drift_detected ? 'DRIFT DETECTED' : 'STABLE'}
          </span>
          <span className="stat-sub">Threshold: 30% drifted features</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Drift Share</span>
          <span className="stat-value">
            {report ? `${(report.drift_share * 100).toFixed(1)}%` : '0%'}
          </span>
          <span className="stat-sub">{report?.drifted_features_count} of {report?.total_features_count} features</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Prediction Drift</span>
          <span className="stat-value" style={{ color: report?.prediction_drift_detected ? 'var(--accent-amber)' : 'var(--text-main)' }}>
            {report?.prediction_drift_detected ? 'Detected' : 'None'}
          </span>
          <span className="stat-sub">Target class distribution stability</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Report ID</span>
          <span className="stat-value" style={{ fontSize: '0.9rem', fontFamily: 'var(--font-mono)' }}>
            {report?.id.slice(0, 8)}...
          </span>
          <span className="stat-sub">{report ? new Date(report.generated_at).toLocaleTimeString() : '-'}</span>
        </div>
      </div>

      {/* Feature Drift Breakdown Table */}
      <div className="stat-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Feature-Level Statistical Test Breakdown</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Status</th>
                <th>Test Score / Statistic</th>
                <th>Statistical Test</th>
                <th>Significance Threshold (p-val)</th>
              </tr>
            </thead>
            <tbody>
              {report?.feature_details.map((f) => (
                <tr key={f.feature_name}>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{f.feature_name}</td>
                  <td>
                    {f.drift_detected ? (
                      <span className="badge badge-candidate">DRIFTED</span>
                    ) : (
                      <span className="badge badge-prod">STABLE</span>
                    )}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{f.drift_score.toFixed(4)}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{f.stat_test}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{f.threshold}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
