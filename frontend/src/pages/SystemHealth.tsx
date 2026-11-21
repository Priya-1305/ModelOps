import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SystemHealth as HealthType } from '../types';
import { Server, CheckCircle2, Clock, Shield, RefreshCw } from 'lucide-react';

export const SystemHealth: React.FC = () => {
  const [liveness, setLiveness] = useState<any | null>(null);
  const [readiness, setReadiness] = useState<HealthType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    try {
      setLoading(true);
      const [live, ready] = await Promise.all([api.getHealth(), api.getReadiness()]);
      setLiveness(live);
      setReadiness(ready);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>System Health & Infrastructure</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            FastAPI process status, in-memory model warming, database connectivity, and readiness probes.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={loadHealth}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      <div className="grid-2">
        <div className="stat-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="var(--accent-blue)" /> Liveness Probe (/api/v1/health)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Status:</span>
              <span className="badge badge-prod">{liveness?.status || 'HEALTHY'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Environment:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{liveness?.environment || 'development'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Service:</span>
              <span>{liveness?.service || 'ModelOps Platform'}</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={18} color="var(--accent-emerald)" /> Readiness Probe (/api/v1/ready)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Readiness:</span>
              <span className={`badge ${readiness?.ready ? 'badge-prod' : 'badge-candidate'}`}>
                {readiness?.status || 'READY'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Active Production Model:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{readiness?.active_model || 'breast_cancer_classifier'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Active In-Memory Version:</span>
              <span className="badge badge-staging">v{readiness?.active_version || '1.0'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Process Uptime:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{readiness?.uptime_seconds ? `${readiness.uptime_seconds}s` : '-'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
