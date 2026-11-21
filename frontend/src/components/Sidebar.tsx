import React from 'react';
import {
  LayoutDashboard,
  Layers,
  FlaskConical,
  Cpu,
  PlaySquare,
  Activity,
  AlertTriangle,
  Rocket,
  ShieldAlert,
  Server
} from 'lucide-react';

interface Props {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export const Sidebar: React.FC<Props> = ({ currentPage, onNavigate }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'models', label: 'Model Registry', icon: Layers },
    { id: 'experiments', label: 'Experiments', icon: FlaskConical },
    { id: 'training-runs', label: 'Training Pipeline', icon: Cpu },
    { id: 'prediction-explorer', label: 'Prediction Explorer', icon: PlaySquare },
    { id: 'monitoring', label: 'Observability', icon: Activity },
    { id: 'drift-reports', label: 'Drift Reports', icon: AlertTriangle },
    { id: 'deployments', label: 'Deployments', icon: Rocket },
    { id: 'health', label: 'System Health', icon: Server },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          backgroundColor: 'var(--accent-blue)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 800,
          color: '#ffffff',
          fontSize: '1.1rem'
        }}>
          M
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.02em' }}>ModelOps</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ML Platform v1.0</div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id || (item.id === 'models' && currentPage === 'model-details');
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                padding: '10px 14px',
                borderRadius: '6px',
                border: 'none',
                background: isActive ? 'var(--bg-surface-hover)' : 'transparent',
                color: isActive ? 'var(--accent-blue)' : 'var(--text-muted)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent-blue)' : 'var(--text-dim)'} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-emerald)' }}></span>
          <span>Engine Active (Port 8000)</span>
        </div>
      </div>
    </aside>
  );
};
