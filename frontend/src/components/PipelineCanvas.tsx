import React, { useState, useEffect } from 'react';
import { Play, CheckCircle2, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';
import { apiFetch } from '../services/api.ts';

export default function PipelineCanvas() {
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [activePlan, setActivePlan] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchPipelines = async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch('/v1/pipelines');
      setPipelines(data);
    } catch (err) {
      console.error('Error fetching pipelines:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPipelines();
  }, []);

  const handleRunPipeline = async (dagId: string) => {
    setIsExecuting(true);
    try {
      const plan = await apiFetch('/v1/pipelines/run', {
        method: 'POST',
        body: JSON.stringify({ dag_id: dagId })
      });
      setActivePlan(plan);
      fetchPipelines();
    } catch (err) {
      console.error('Error running pipeline:', err);
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-teal-400" />
        Loading DAG pipelines...
      </div>
    );
  }

  const primaryDag = pipelines[0];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white">Declarative Pipeline DAG Engine</h2>
          <p className="text-xs text-slate-400">Workflow: {primaryDag ? primaryDag.dag_id : 'continuous_retraining_v2'}</p>
        </div>
        <button 
          onClick={() => handleRunPipeline(primaryDag ? primaryDag.dag_id : 'continuous_retraining_v2')}
          disabled={isExecuting}
          className="flex items-center gap-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold px-4 py-2 rounded-lg text-xs transition shadow-md shadow-teal-500/20 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {isExecuting ? 'Executing DAG...' : 'Trigger Execution (POST /v1/pipelines/run)'}
        </button>
      </div>

      {activePlan && (
        <div className="bg-slate-950 border border-teal-500/30 p-4 rounded-xl text-xs space-y-2">
          <div className="flex items-center justify-between text-teal-300 font-bold">
            <span>Latest Execution: {activePlan.run_id}</span>
            <span className="text-emerald-400">● {activePlan.status} ({activePlan.duration_sec.toFixed(3)}s)</span>
          </div>
          <pre className="text-slate-400 font-mono text-[11px] overflow-auto">
            {JSON.stringify(activePlan.task_outputs, null, 2)}
          </pre>
        </div>
      )}

      <div className="flex items-center gap-4 overflow-x-auto p-4 bg-slate-950 rounded-xl border border-slate-800">
        {primaryDag ? (
          primaryDag.tasks.map((task: any, idx: number) => (
            <React.Fragment key={task.task_id}>
              <div className="min-w-[190px] bg-slate-900 border border-slate-700 p-4 rounded-lg shadow">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                  <span>TASK {idx + 1}</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                </div>
                <div className="font-bold text-xs text-slate-200">{task.task_id}</div>
                <div className="text-[11px] text-teal-400 mt-2">Status: SUCCESS</div>
              </div>
              {idx < primaryDag.tasks.length - 1 && <ArrowRight className="w-5 h-5 text-slate-600 flex-shrink-0" />}
            </React.Fragment>
          ))
        ) : (
          <div className="text-xs text-slate-500 p-4">No tasks found.</div>
        )}
      </div>
    </div>
  );
}
