import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ModelSummary } from '../types';
import { Layers, ChevronRight, RefreshCw } from 'lucide-react';

interface Props {
  onSelectModel: (modelName: string) => void;
}

export const ModelRegistry: React.FC<Props> = ({ onSelectModel }) => {
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const res = await api.getModels();
      setModels(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Model Registry</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Managed repository of registered machine learning models, active versions, and stage gates.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadModels}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {models.length === 0 ? (
        <div className="stat-card" style={{ textAlign: 'center', padding: '48px' }}>
          <Layers size={40} color="var(--text-dim)" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>No Registered Models</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '8px' }}>
            Train and register a candidate model from the Training Pipeline to populate the registry.
          </p>
        </div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Model Name</th>
                <th>Production Version</th>
                <th>Total Versions</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id}>
                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                  <td>
                    {m.active_version ? (
                      <span className="badge badge-prod">v{m.active_version} (Prod)</span>
                    ) : (
                      <span className="badge badge-candidate">No Prod Version</span>
                    )}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{m.version_count}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(m.updated_at).toLocaleString()}</td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '4px 12px', fontSize: '0.75rem' }}
                      onClick={() => onSelectModel(m.name)}
                    >
                      Inspect <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
