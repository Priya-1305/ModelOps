import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ModelDetail, ModelVersion } from '../types';
import { ArrowLeft, ShieldCheck, RotateCcw, AlertCircle, CheckCircle, Tag } from 'lucide-react';

interface Props {
  modelName: string;
  onBack: () => void;
}

export const ModelDetails: React.FC<Props> = ({ modelName, onBack }) => {
  const [model, setModel] = useState<ModelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Promotion state
  const [promotingVersion, setPromotingVersion] = useState<string | null>(null);
  const [minF1, setMinF1] = useState(0.85);
  const [minAuc, setMinAuc] = useState(0.85);
  const [force, setForce] = useState(false);

  useEffect(() => {
    loadDetails();
  }, [modelName]);

  const loadDetails = async () => {
    try {
      setLoading(true);
      const res = await api.getModelDetails(modelName);
      setModel(res);
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message });
    } finally {
      setLoading(false);
    }
  };

  const handlePromote = async (version: string) => {
    try {
      setActionMessage(null);
      await api.promoteModel(modelName, version, {
        minimum_f1_score: minF1,
        minimum_roc_auc: minAuc,
        force: force,
        comment: 'Promoted via web dashboard quality gate',
      });
      setActionMessage({ type: 'success', text: `Version ${version} promoted to PRODUCTION successfully!` });
      setPromotingVersion(null);
      loadDetails();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message });
    }
  };

  const handleRollback = async () => {
    if (!confirm('Are you sure you want to rollback the active production model to the previous stable release?')) return;
    try {
      setActionMessage(null);
      const res = await api.rollbackModel(modelName, { comment: 'Rollback initiated from web UI' });
      setActionMessage({ type: 'success', text: `Model successfully rolled back to version ${res.version}!` });
      loadDetails();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message });
    }
  };

  if (!model && !loading) {
    return (
      <div>
        <button className="btn btn-secondary" onClick={onBack}><ArrowLeft size={16} /> Back to Models</button>
        <div style={{ marginTop: '20px', color: 'var(--accent-rose)' }}>Model '{modelName}' not found.</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn btn-secondary" onClick={onBack}>
            <ArrowLeft size={16} /> Back
          </button>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>{model?.name}</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Active version: <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>v{model?.active_version || 'None'}</span>
            </p>
          </div>
        </div>
        <button className="btn btn-danger" onClick={handleRollback}>
          <RotateCcw size={16} /> Rollback Production
        </button>
      </div>

      {actionMessage && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: '6px',
            backgroundColor: actionMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            border: `1px solid ${actionMessage.type === 'success' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)'}`,
            color: actionMessage.type === 'success' ? '#34d399' : '#fb7185',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          {actionMessage.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {/* Version History Table */}
      <div className="stat-card">
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '8px' }}>Version History & Quality Gates</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Version</th>
                <th>Stage</th>
                <th>Validation F1</th>
                <th>Validation ROC-AUC</th>
                <th>Test Accuracy</th>
                <th>Created At</th>
                <th>Controlled Promotion</th>
              </tr>
            </thead>
            <tbody>
              {model?.versions.map((ver) => (
                <tr key={ver.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>v{ver.version}</td>
                  <td>
                    <span className={`badge ${
                      ver.stage === 'production' ? 'badge-prod' :
                      ver.stage === 'candidate' ? 'badge-candidate' : 'badge-archived'
                    }`}>
                      {ver.stage}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{ver.metrics.val_f1_score?.toFixed(4) || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{ver.metrics.val_roc_auc?.toFixed(4) || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{ver.metrics.test_accuracy?.toFixed(4) || '-'}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(ver.created_at).toLocaleDateString()}</td>
                  <td>
                    {ver.stage === 'production' ? (
                      <span style={{ color: 'var(--accent-emerald)', fontSize: '0.8rem', fontWeight: 600 }}>Active Target</span>
                    ) : (
                      <button
                        className="btn btn-primary"
                        style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                        onClick={() => setPromotingVersion(ver.version)}
                      >
                        <ShieldCheck size={14} /> Promote
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Promotion Quality Gate Modal */}
      {promotingVersion && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="stat-card" style={{ width: '480px', maxWidth: '90%', gap: '16px' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Promote Model to Production</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Promoting version <code style={{ color: 'var(--accent-cyan)' }}>v{promotingVersion}</code>. 
              The platform evaluates candidate metrics against acceptance criteria before promoting.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.825rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Minimum Validation F1 Gate
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={minF1}
                  onChange={(e) => setMinF1(parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    fontFamily: 'var(--font-mono)'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.825rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Minimum Validation ROC-AUC Gate
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={minAuc}
                  onChange={(e) => setMinAuc(parseFloat(e.target.value) || 0)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    fontFamily: 'var(--font-mono)'
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                <input
                  type="checkbox"
                  id="force-chk"
                  checked={force}
                  onChange={(e) => setForce(e.target.checked)}
                />
                <label htmlFor="force-chk" style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                  Override gate checks (emergency force promote)
                </label>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
              <button className="btn btn-secondary" onClick={() => setPromotingVersion(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={() => handlePromote(promotingVersion)}>
                Confirm Promotion
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
