import React from 'react';
import { Play, CheckCircle2, ArrowRight } from 'lucide-react';

export default function PipelineCanvas() {
  const steps = [
    { id: '1', name: 'Ingest Batch Features', type: 'FEATURE_STORE', status: 'SUCCESS', duration: '1.2s' },
    { id: '2', name: 'Point-in-Time Join', type: 'JOIN_ENGINE', status: 'SUCCESS', duration: '3.4s' },
    { id: '3', name: 'Distributed HPO (Hyperband)', type: 'TRAINING', status: 'SUCCESS', duration: '45.1s' },
    { id: '4', name: 'Validate Model Contract', type: 'REGISTRY', status: 'SUCCESS', duration: '0.8s' },
    { id: '5', name: 'Canary Deployment (10%)', type: 'SERVING', status: 'RUNNING', duration: 'Live' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold">Pipeline DAG Visualizer</h2>
          <p className="text-xs text-slate-400">Workflow: continuous_retraining_v2</p>
        </div>
        <button className="flex items-center gap-2 bg-teal-600 hover:bg-teal-500 text-slate-950 font-semibold px-4 py-2 rounded-lg text-sm transition">
          <Play className="w-4 h-4 fill-current" /> Trigger Execution
        </button>
      </div>

      <div className="flex items-center gap-4 overflow-x-auto p-4 bg-slate-950/60 rounded-lg border border-slate-800/80">
        {steps.map((s, idx) => (
          <React.Fragment key={s.id}>
            <div className="min-w-[200px] bg-slate-900 border border-slate-700 p-4 rounded-lg shadow">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{s.type}</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              </div>
              <div className="font-medium text-sm text-slate-200">{s.name}</div>
              <div className="text-xs text-teal-400 mt-2">{s.duration}</div>
            </div>
            {idx < steps.length - 1 && <ArrowRight className="w-5 h-5 text-slate-600 flex-shrink-0" />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
