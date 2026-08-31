import { useState, useEffect } from 'react';
import { 
  Activity, 
  Database, 
  GitBranch, 
  TrendingUp, 
  LogOut, 
  Zap
} from 'lucide-react';
import ModelMetricsView from './components/ModelMetricsView.tsx';
import PipelineCanvas from './components/PipelineCanvas.tsx';
import DriftDashboard from './components/DriftDashboard.tsx';
import FeatureCatalog from './components/FeatureCatalog.tsx';
import EndToEndDemo from './components/EndToEndDemo.tsx';
import LoginModal from './components/LoginModal.tsx';
import { apiFetch } from './services/api.ts';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<string>('admin');
  const [activeTab, setActiveTab] = useState<'demo' | 'metrics' | 'pipelines' | 'drift' | 'features'>('demo');
  const [clusterHealthy, setClusterHealthy] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem('manta_token');
    const user = localStorage.getItem('manta_user');
    if (token) {
      setIsAuthenticated(true);
      if (user) setCurrentUser(user);
    }
    apiFetch('/health')
      .then(res => setClusterHealthy(res.status === 'HEALTHY'))
      .catch(() => setClusterHealthy(false));
  }, []);

  const handleLogout = async () => {
    try {
      await apiFetch('/v1/auth/logout', { method: 'POST' });
    } catch {}
    localStorage.removeItem('manta_token');
    localStorage.removeItem('manta_user');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return (
      <LoginModal 
        onSuccess={(username) => {
          setIsAuthenticated(true);
          setCurrentUser(username);
        }} 
      />
    );
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
            <div className="h-9 w-9 rounded-xl bg-teal-500 flex items-center justify-center font-black text-slate-950 text-xl shadow-lg shadow-teal-500/20">
              M
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight text-white">Manta ML</h1>
              <p className="text-xs text-teal-400 font-medium">Distributed ML Systems</p>
            </div>
          </div>

          <nav className="p-4 space-y-1.5">
            <button 
              onClick={() => setActiveTab('demo')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition ${activeTab === 'demo' ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20' : 'text-teal-300 hover:bg-slate-800 hover:text-white'}`}
            >
              <Zap className="w-4 h-4 fill-current" />
              E2E Workflow Demo
            </button>

            <button 
              onClick={() => setActiveTab('metrics')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${activeTab === 'metrics' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <Activity className="w-4 h-4" />
              Inference & Metrics
            </button>

            <button 
              onClick={() => setActiveTab('pipelines')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${activeTab === 'pipelines' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <GitBranch className="w-4 h-4" />
              Pipeline DAGs
            </button>

            <button 
              onClick={() => setActiveTab('drift')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${activeTab === 'drift' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <TrendingUp className="w-4 h-4" />
              Drift & Monitoring
            </button>

            <button 
              onClick={() => setActiveTab('features')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${activeTab === 'features' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <Database className="w-4 h-4" />
              Feature Store
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-mono">User: {currentUser}</span>
            <button onClick={handleLogout} className="flex items-center gap-1 text-rose-400 hover:text-rose-300 transition text-[11px] font-semibold">
              <LogOut className="w-3.5 h-3.5" /> Logout
            </button>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>Cluster: manta-primary</span>
            <span className={`h-2 w-2 rounded-full ${clusterHealthy ? 'bg-teal-400 animate-pulse' : 'bg-rose-500'}`}></span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-slate-900/50 border-b border-slate-800 px-8 flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Cluster Status:</span>
            {clusterHealthy ? (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span> Online (4 Workers)
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                Disconnected
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-teal-400 px-3 py-1.5 rounded-lg border border-slate-700 transition">
              Swagger API Docs
            </a>
            <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-md border border-slate-700 font-mono">
              v1.0.0-enterprise
            </span>
          </div>
        </header>

        <div className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'demo' && <EndToEndDemo />}
          {activeTab === 'metrics' && <ModelMetricsView />}
          {activeTab === 'pipelines' && <PipelineCanvas />}
          {activeTab === 'drift' && <DriftDashboard />}
          {activeTab === 'features' && <FeatureCatalog />}
        </div>
      </main>
    </div>
  );
}
