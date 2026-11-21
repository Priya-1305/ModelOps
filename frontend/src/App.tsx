import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { ModelRegistry } from './pages/ModelRegistry';
import { ModelDetails } from './pages/ModelDetails';
import { Experiments } from './pages/Experiments';
import { TrainingRuns } from './pages/TrainingRuns';
import { PredictionExplorer } from './pages/PredictionExplorer';
import { Monitoring } from './pages/Monitoring';
import { DriftReports } from './pages/DriftReports';
import { Deployments } from './pages/Deployments';
import { SystemHealth } from './pages/SystemHealth';
import { Bell, Terminal } from 'lucide-react';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('overview');
  const [selectedModel, setSelectedModel] = useState<string>('breast_cancer_classifier');

  const handleSelectModel = (name: string) => {
    setSelectedModel(name);
    setCurrentPage('model-details');
  };

  const renderContent = () => {
    switch (currentPage) {
      case 'overview':
        return <Overview onNavigate={setCurrentPage} />;
      case 'models':
        return <ModelRegistry onSelectModel={handleSelectModel} />;
      case 'model-details':
        return <ModelDetails modelName={selectedModel} onBack={() => setCurrentPage('models')} />;
      case 'experiments':
        return <Experiments />;
      case 'training-runs':
        return <TrainingRuns />;
      case 'prediction-explorer':
        return <PredictionExplorer />;
      case 'monitoring':
        return <Monitoring />;
      case 'drift-reports':
        return <DriftReports />;
      case 'deployments':
        return <Deployments />;
      case 'health':
        return <SystemHealth />;
      default:
        return <Overview onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="layout-container">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <div className="content-area">
        <header className="top-navbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <span>ModelOps</span>
            <span>/</span>
            <span style={{ color: 'var(--text-main)', fontWeight: 600, textTransform: 'capitalize' }}>
              {currentPage.replace('-', ' ')}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span className="badge badge-prod">Live Serving</span>
            <a
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
            >
              <Terminal size={14} /> API Docs
            </a>
          </div>
        </header>
        <main className="page-content">{renderContent()}</main>
      </div>
    </div>
  );
};

export default App;
