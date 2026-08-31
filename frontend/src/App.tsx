import React, { useState } from 'react';
import { 
  Activity, 
  Database, 
  Layers, 
  Cpu, 
  GitBranch, 
  TrendingUp, 
  ShieldAlert, 
  Server, 
  Settings 
} from 'lucide-react';
import PipelineCanvas from './components/PipelineCanvas.tsx';
import ModelMetricsView from './components/ModelMetricsView.tsx';
import DriftDashboard from './components/DriftDashboard.tsx';
import FeatureCatalog from './components/FeatureCatalog.tsx';

export default function App() {
  const [activeTab, setActiveTab] = useState<'metrics' | 'pipelines' | 'drift' | 'features'>('metrics');

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
            <div className="h-8 w-8 rounded-lg bg-teal-500 flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-teal-500/20">
              M
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight">Manta ML</h1>
              <p className="text-xs text-teal-400 font-medium">Distributed ML Systems</p>
            </div>
          </div>

          <nav className="p-4 space-y-1.5">
            <button 
              onClick={() => setActiveTab('metrics')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'metrics' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <Activity className="w-4 h-4" />
              Inference & Metrics
            </button>

            <button 
              onClick={() => setActiveTab('pipelines')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'pipelines' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <GitBranch className="w-4 h-4" />
              Pipeline DAGs
            </button>

            <button 
              onClick={() => setActiveTab('drift')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'drift' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <TrendingUp className="w-4 h-4" />
              Drift & Monitoring
            </button>

            <button 
              onClick={() => setActiveTab('features')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'features' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
              <Database className="w-4 h-4" />
              Feature Store
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex items-center justify-between">
          <span>Cluster: manta-primary</span>
          <span className="h-2 w-2 rounded-full bg-teal-400 animate-pulse"></span>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-slate-900/50 border-b border-slate-800 px-8 flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-4">
            <span className="text-sm font-semibold text-slate-300">Cluster Status:</span>
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ● Healthy (4 Workers)
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-md border border-slate-700">
              v1.0.0-enterprise
            </span>
          </div>
        </header>

        {/* View Switcher */}
        <div className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'metrics' && <ModelMetricsView />}
          {activeTab === 'pipelines' && <PipelineCanvas />}
          {activeTab === 'drift' && <DriftDashboard />}
          {activeTab === 'features' && <FeatureCatalog />}
        </div>
      </main>
    </div>
  );
}
