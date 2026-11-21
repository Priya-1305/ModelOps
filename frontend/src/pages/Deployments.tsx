import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ModelDetail, ModelSummary } from '../types';
import { Rocket, ShieldCheck, RotateCcw, RefreshCw, Server } from 'lucide-react';

export const Deployments: React.FC = () => {
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDeployments();
  }, []);

  const loadDeployments = async () => {
    try {
      setLoading(true);
      const res = await api.getModels();
      setModels(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Deployment Management</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Production release environments, active serving versions, and rollback readiness.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadDeployments}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      <div className="stat-card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Active Serving Deployments</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Service Name</th>
                <th>Target Environment</th>
                <th>Active Serving Version</th>
                <th>Health Status</th>
                <th>Rollback Target Available</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id}>
                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                  <td><span className="badge badge-prod">PRODUCTION</span></td>
                  <td>
                    {m.active_version ? (
                      <span className="badge badge-staging">v{m.active_version}</span>
                    ) : (
                      <span className="badge badge-candidate">Warming Up</span>
                    )}
                  </td>
                  <td>
                    <span style={{ color: 'var(--accent-emerald)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      ● Serving In-Memory
                    </span>
                  </td>
                  <td>
                    {m.version_count > 1 ? (
                      <span style={{ color: 'var(--accent-cyan)' }}>Yes ({m.version_count - 1} standby)</span>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
