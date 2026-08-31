import React, { useState, useEffect } from 'react';
import { TrendingUp, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { apiFetch } from '../services/api.ts';

export default function DriftDashboard() {
  const [driftReports, setDriftReports] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchDrift = async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch('/v1/monitoring/drift');
      setDriftReports(data);
    } catch (err) {
      console.error('Error fetching drift data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDrift();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-teal-400" />
        Evaluating Kolmogorov-Smirnov and Wasserstein drift metrics...
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white">Statistical Model & Feature Drift Monitoring</h2>
          <p className="text-xs text-slate-400">Continuous distribution divergence evaluation for model: fraud_detector</p>
        </div>
        <button onClick={fetchDrift} className="text-xs font-semibold bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition flex items-center gap-1.5">
          <RefreshCw className="w-3.5 h-3.5" /> Re-evaluate Drift
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {driftReports.length === 0 ? (
          <div className="text-xs text-slate-500">No drift statistics recorded.</div>
        ) : (
          driftReports.map((rep: any) => (
            <div key={rep.feature_name} className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-200">{rep.feature_name}</span>
                {rep.drift_detected ? (
                  <span className="flex items-center gap-1 text-rose-400 text-xs font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                    <AlertTriangle className="w-3.5 h-3.5" /> DRIFT DETECTED
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-emerald-400 text-xs font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    <CheckCircle2 className="w-3.5 h-3.5" /> HEALTHY
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-400 font-mono">Detector: {rep.detector}</div>
              <div className="text-xs text-teal-400 font-mono">D-Statistic: {rep.metric_value} (p={rep.p_value})</div>
              <div className="text-[11px] text-slate-500">Threshold: {rep.threshold}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
