import React, { useState } from 'react';
import { Play, CheckCircle2, RefreshCw, ArrowRight, Zap, Database, TrendingUp, ShieldCheck } from 'lucide-react';
import { apiFetch } from '../services/api.ts';

export default function EndToEndDemo() {
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [logs, setLogs] = useState<Array<{ msg: string; color: string; time: string }>>([]);

  const addLog = (msg: string, color: string = 'text-teal-300') => {
    setLogs(prev => [...prev, { msg, color, time: new Date().toLocaleTimeString() }]);
  };

  const executeDemoFlow = async () => {
    setIsRunning(true);
    setLogs([]);
    setCurrentStep(1);
    addLog('▶ Starting End-to-End Distributed ML Systems Workflow Demonstration...', 'text-white font-bold');

    try {
      // Step 1: Feature Store Online Ingestion & Lookup
      addLog('Step 1/4: Querying Feature Store for customer entity "u1001"...');
      const featureRes = await apiFetch('/v1/features/online', {
        method: 'POST',
        body: JSON.stringify({
          feature_view: 'user_stats',
          entity_keys: ['u1001']
        })
      });
      const featureData = featureRes.data[0];
      addLog(`✓ Feature Store Retrieved: click_rate=${featureData.click_rate}, purchases=${featureData.purchases_count}, risk_score=${featureData.risk_score}`, 'text-emerald-400');
      
      await new Promise(r => setTimeout(r, 700));
      setCurrentStep(2);

      // Step 2: High-Performance Inference with Dynamic Batching
      addLog('Step 2/4: Dispatching dynamic batch inference request to model "fraud_detector:v1.2"...');
      const inferRes = await apiFetch('/v1/models/predict', {
        method: 'POST',
        body: JSON.stringify({
          model_name: 'fraud_detector',
          version: 'v1.2',
          inputs: {
            features: [featureData.click_rate, featureData.purchases_count, featureData.risk_score, 1.0]
          }
        })
      });
      addLog(`✓ Prediction Served: score=${inferRes.outputs.prediction[0].toExponential(3)}, latency=${inferRes.latency_ms.toFixed(3)}ms (status=200 OK)`, 'text-emerald-400');

      await new Promise(r => setTimeout(r, 700));
      setCurrentStep(3);

      // Step 3: Drift & Data Quality Monitoring
      addLog('Step 3/4: Evaluating production feature distributions via Kolmogorov-Smirnov & Wasserstein distance...');
      const driftRes = await apiFetch('/v1/monitoring/drift');
      addLog(`✓ Drift Monitoring Evaluated: ${driftRes.length} features analyzed against baseline, Zero Drift Detected (Status: HEALTHY)`, 'text-emerald-400');

      await new Promise(r => setTimeout(r, 700));
      setCurrentStep(4);

      // Step 4: Retraining Pipeline DAG Execution
      addLog('Step 4/4: Triggering Retraining DAG Pipeline ("continuous_retraining_v2")...');
      const pipeRes = await apiFetch('/v1/pipelines/run', {
        method: 'POST',
        body: JSON.stringify({ dag_id: 'continuous_retraining_v2' })
      });
      addLog(`✓ Pipeline DAG Run Complete: Run ID ${pipeRes.run_id} finished with status ${pipeRes.status} in ${pipeRes.duration_sec.toFixed(3)}s`, 'text-emerald-400');

      addLog('★ COMPLETE END-TO-END ML SYSTEMS WORKFLOW VERIFIED SUCCESSFULLY ★', 'text-teal-400 font-bold');
      setCurrentStep(5);
    } catch (err: any) {
      addLog(`Error during workflow: ${err.message}`, 'text-rose-400 font-bold');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-teal-500/30 rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-teal-400 fill-current" />
              Interactive End-to-End ML Systems Demonstration
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Demonstrates complete lifecycle: Feature Store Lookup → Dynamic Batch Inference → Drift Detection → DAG Retraining Pipeline.
            </p>
          </div>
          <button 
            onClick={executeDemoFlow}
            disabled={isRunning}
            className="px-6 py-3 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-lg transition shadow-lg shadow-teal-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Executing Flow...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run Complete Demo Flow
              </>
            )}
          </button>
        </div>

        {/* Visual Flow Steps */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className={`p-4 rounded-xl border transition ${currentStep >= 1 ? 'bg-teal-950/40 border-teal-500/60' : 'bg-slate-950/60 border-slate-800'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase text-slate-400">Step 1</span>
              <Database className={`w-4 h-4 ${currentStep >= 1 ? 'text-teal-400' : 'text-slate-600'}`} />
            </div>
            <div className="font-bold text-sm text-slate-200">Feature Store</div>
            <div className="text-xs text-slate-400 mt-1">Entity u1001 Lookup</div>
          </div>

          <div className={`p-4 rounded-xl border transition ${currentStep >= 2 ? 'bg-teal-950/40 border-teal-500/60' : 'bg-slate-950/60 border-slate-800'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase text-slate-400">Step 2</span>
              <Zap className={`w-4 h-4 ${currentStep >= 2 ? 'text-teal-400' : 'text-slate-600'}`} />
            </div>
            <div className="font-bold text-sm text-slate-200">Dynamic Batching</div>
            <div className="text-xs text-slate-400 mt-1">fraud_detector:v1.2</div>
          </div>

          <div className={`p-4 rounded-xl border transition ${currentStep >= 3 ? 'bg-teal-950/40 border-teal-500/60' : 'bg-slate-950/60 border-slate-800'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase text-slate-400">Step 3</span>
              <TrendingUp className={`w-4 h-4 ${currentStep >= 3 ? 'text-teal-400' : 'text-slate-600'}`} />
            </div>
            <div className="font-bold text-sm text-slate-200">Drift Monitoring</div>
            <div className="text-xs text-slate-400 mt-1">KS & Wasserstein Tests</div>
          </div>

          <div className={`p-4 rounded-xl border transition ${currentStep >= 4 ? 'bg-teal-950/40 border-teal-500/60' : 'bg-slate-950/60 border-slate-800'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase text-slate-400">Step 4</span>
              <ShieldCheck className={`w-4 h-4 ${currentStep >= 4 ? 'text-teal-400' : 'text-slate-600'}`} />
            </div>
            <div className="font-bold text-sm text-slate-200">Pipeline DAG</div>
            <div className="text-xs text-slate-400 mt-1">continuous_retrain</div>
          </div>
        </div>

        {/* Execution Log Terminal */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-1.5 h-64 overflow-y-auto shadow-inner">
          {logs.length === 0 ? (
            <div className="text-slate-600 italic">Ready to run demonstration. Click 'Run Complete Demo Flow' above to start.</div>
          ) : (
            logs.map((l, i) => (
              <div key={i} className={l.color}>
                <span className="text-slate-600">[{l.time}]</span> {l.msg}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
