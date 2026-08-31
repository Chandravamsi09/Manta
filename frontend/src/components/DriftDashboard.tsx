import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function DriftDashboard() {
  const driftStats = [
    { feature: 'user_age', method: 'Kolmogorov-Smirnov', metric: '0.012', p_val: '0.88', status: 'HEALTHY' },
    { feature: 'transaction_amt', method: 'Wasserstein-1', metric: '0.045', p_val: '-', status: 'HEALTHY' },
    { feature: 'device_os', method: 'Chi-Square', metric: '1.201', p_val: '0.45', status: 'HEALTHY' },
    { feature: 'query_embedding', method: 'Cosine Centroid', metric: '0.031', p_val: '-', status: 'HEALTHY' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
      <h2 className="text-lg font-semibold">Distribution Drift Monitoring</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {driftStats.map((item) => (
          <div key={item.feature} className="bg-slate-950/60 border border-slate-800 p-4 rounded-lg flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-slate-200">{item.feature}</div>
              <div className="text-xs text-slate-400">{item.method} — Value: {item.metric}</div>
            </div>
            <div className="flex items-center gap-1 text-emerald-400 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4" /> Healthy
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
