import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { PredictionResponse, PredictionLog } from '../types';
import { Play, Sparkles, Clock, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

const BENIGN_PRESET: Record<string, number> = {
  mean_radius: 13.54, mean_texture: 14.36, mean_perimeter: 87.46, mean_area: 566.3, mean_smoothness: 0.09779,
  mean_compactness: 0.08129, mean_concavity: 0.06664, mean_concave_points: 0.04781, mean_symmetry: 0.1885, mean_fractal_dimension: 0.05766,
  radius_error: 0.2699, texture_error: 0.7886, perimeter_error: 2.058, area_error: 23.56, smoothness_error: 0.008462,
  compactness_error: 0.0146, concavity_error: 0.02387, concave_points_error: 0.01315, symmetry_error: 0.0198, fractal_dimension_error: 0.0023,
  worst_radius: 15.11, worst_texture: 19.26, worst_perimeter: 99.7, worst_area: 711.2, worst_smoothness: 0.144,
  worst_compactness: 0.1773, worst_concavity: 0.239, worst_concave_points: 0.1288, worst_symmetry: 0.2977, worst_fractal_dimension: 0.07259
};

const MALIGNANT_PRESET: Record<string, number> = {
  mean_radius: 20.57, mean_texture: 17.77, mean_perimeter: 132.9, mean_area: 1326.0, mean_smoothness: 0.08474,
  mean_compactness: 0.07864, mean_concavity: 0.0869, mean_concave_points: 0.07017, mean_symmetry: 0.1812, mean_fractal_dimension: 0.05667,
  radius_error: 0.5435, texture_error: 0.7339, perimeter_error: 3.398, area_error: 74.08, smoothness_error: 0.005225,
  compactness_error: 0.01308, concavity_error: 0.0186, concave_points_error: 0.0134, symmetry_error: 0.01389, fractal_dimension_error: 0.003532,
  worst_radius: 24.99, worst_texture: 23.41, worst_perimeter: 158.8, worst_area: 1956.0, worst_smoothness: 0.1238,
  worst_compactness: 0.1866, worst_concavity: 0.2416, worst_concave_points: 0.186, worst_symmetry: 0.275, worst_fractal_dimension: 0.08902
};

export const PredictionExplorer: React.FC = () => {
  const [features, setFeatures] = useState<Record<string, number>>(BENIGN_PRESET);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [logs, setLogs] = useState<PredictionLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const data = await api.getPredictionLogs();
      setLogs(data);
    } catch (_) {}
  };

  const handlePredict = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.predict(features);
      setResult(res);
      await loadLogs();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Prediction Explorer</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Interactive real-time model inference and historical request auditing.
        </p>
      </div>

      {/* Preset Toolbar */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Load Test Presets:</span>
        <button className="btn btn-secondary" onClick={() => setFeatures(BENIGN_PRESET)}>
          <Sparkles size={14} color="var(--accent-emerald)" /> Benign Tumor Sample
        </button>
        <button className="btn btn-secondary" onClick={() => setFeatures(MALIGNANT_PRESET)}>
          <Sparkles size={14} color="var(--accent-rose)" /> Malignant Tumor Sample
        </button>
      </div>

      <div className="grid-2">
        {/* Input Parameters Panel */}
        <div className="stat-card" style={{ gap: '16px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Feature Input Vector (30 features)</h3>
          <div style={{ maxHeight: '380px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '6px' }}>
            {Object.keys(features).map((key) => (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label style={{ fontSize: '0.775rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                  {key}
                </label>
                <input
                  type="number"
                  step="any"
                  value={features[key]}
                  onChange={(e) => setFeatures({ ...features, [key]: parseFloat(e.target.value) || 0 })}
                  style={{
                    width: '120px',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.8rem',
                  }}
                />
              </div>
            ))}
          </div>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading} style={{ justifyContent: 'center' }}>
            <Play size={16} /> {loading ? 'Computing Inference...' : 'Send Prediction Request'}
          </button>
          {error && <div style={{ color: 'var(--accent-rose)', fontSize: '0.85rem' }}>{error}</div>}
        </div>

        {/* Inference Result Panel */}
        <div className="stat-card" style={{ gap: '16px', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Real-Time Inference Output</h3>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{
                padding: '20px',
                borderRadius: '8px',
                backgroundColor: result.prediction === 1 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                border: `1px solid ${result.prediction === 1 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Classification</span>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, color: result.prediction === 1 ? '#34d399' : '#fb7185' }}>
                    {result.prediction_label.toUpperCase()}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Class Value</span>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    [{result.prediction}]
                  </div>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Class Probabilities</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                  {Object.entries(result.probabilities).map(([cls, prob]) => (
                    <div key={cls}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '2px' }}>
                        <span>{cls}</span>
                        <span style={{ fontFamily: 'var(--font-mono)' }}>{(prob * 100).toFixed(2)}%</span>
                      </div>
                      <div style={{ height: '6px', backgroundColor: 'var(--bg-surface)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%',
                          width: `${prob * 100}%`,
                          backgroundColor: cls === 'benign' ? 'var(--accent-emerald)' : 'var(--accent-rose)'
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                <span>Latency: <strong style={{ color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>{result.latency_ms} ms</strong></span>
                <span>Version: <strong style={{ color: 'var(--accent-cyan)' }}>v{result.model_version}</strong></span>
                <span>Correlation: <code style={{ fontSize: '0.75rem' }}>{result.correlation_id.slice(0, 8)}</code></span>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '40px 0' }}>
              Adjust features or pick a preset, then click Send Prediction Request.
            </div>
          )}
        </div>
      </div>

      {/* Historical Prediction Log Table */}
      <div className="stat-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Prediction Audit Log</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={loadLogs}>
            <RefreshCw size={14} /> Refresh Logs
          </button>
        </div>
        {logs.length === 0 ? (
          <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '24px' }}>No prediction logs recorded yet.</div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Correlation ID</th>
                  <th>Model Version</th>
                  <th>Prediction</th>
                  <th>Latency</th>
                </tr>
              </thead>
              <tbody>
                {logs.slice(0, 10).map((l) => (
                  <tr key={l.id}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{new Date(l.timestamp).toLocaleTimeString()}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{l.correlation_id}</td>
                    <td><span className="badge badge-staging">v{l.model_version}</span></td>
                    <td>
                      <span className={`badge ${l.prediction === 1 ? 'badge-prod' : 'badge-candidate'}`}>
                        {l.prediction_label}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{l.latency_ms.toFixed(2)} ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
