import React from 'react';
import { Activity, Zap, Clock, ShieldCheck } from 'lucide-react';

export default function ModelMetricsView() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase">Serving QPS</span>
            <Zap className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">4,820 <span className="text-xs text-slate-400 font-normal">req/s</span></div>
          <span className="text-xs text-teal-400 mt-2 block">+12.4% vs last hour</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase">p95 Latency</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">1.42 <span className="text-xs text-slate-400 font-normal">ms</span></div>
          <span className="text-xs text-emerald-400 mt-2 block">Dynamic Batching: ON</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase">Active Deployments</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">12 <span className="text-xs text-slate-400 font-normal">Models</span></div>
          <span className="text-xs text-blue-400 mt-2 block">2 Canary Routes</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase">Governance</span>
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">100% <span className="text-xs text-slate-400 font-normal">ML-BOM</span></div>
          <span className="text-xs text-indigo-400 mt-2 block">Zero CVE Alerts</span>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Production Model Deployments</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs text-slate-400 border-b border-slate-800 uppercase">
              <tr>
                <th className="pb-3">Model Name</th>
                <th className="pb-3">Version</th>
                <th className="pb-3">Stage</th>
                <th className="pb-3">Worker Backend</th>
                <th className="pb-3">Avg Latency</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              <tr>
                <td className="py-3.5 font-medium">fraud_detector</td>
                <td className="py-3.5 text-slate-400">v1.2.0</td>
                <td className="py-3.5"><span className="px-2 py-0.5 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PRODUCTION</span></td>
                <td className="py-3.5 text-slate-400">ONNX Runtime (GPU)</td>
                <td className="py-3.5 text-slate-300">1.25 ms</td>
                <td className="py-3.5 text-teal-400 font-semibold">Ready</td>
              </tr>
              <tr>
                <td className="py-3.5 font-medium">recommendation_ranker</td>
                <td className="py-3.5 text-slate-400">v2.0.1</td>
                <td className="py-3.5"><span className="px-2 py-0.5 rounded text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20">CANARY (20%)</span></td>
                <td className="py-3.5 text-slate-400">PyTorch C++ JIT</td>
                <td className="py-3.5 text-slate-300">3.18 ms</td>
                <td className="py-3.5 text-teal-400 font-semibold">Ready</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
