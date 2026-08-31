import React, { useState, useEffect } from 'react';
import { Database, Zap, RefreshCw } from 'lucide-react';
import { apiFetch } from '../services/api.ts';

export default function FeatureCatalog() {
  const [featureViews, setFeatureViews] = useState<any[]>([]);
  const [lookupKey, setLookupKey] = useState<string>('u1001');
  const [lookupResult, setLookupResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchFeatures = async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch('/v1/features/views');
      setFeatureViews(data);
    } catch (err) {
      console.error('Error fetching feature views:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFeatures();
  }, []);

  const handleLookup = async () => {
    try {
      const res = await apiFetch('/v1/features/online', {
        method: 'POST',
        body: JSON.stringify({
          feature_view: 'user_stats',
          entity_keys: [lookupKey]
        })
      });
      setLookupResult(res.data[0]);
    } catch (err: any) {
      setLookupResult({ error: err.message });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-teal-400" />
        Loading dual-tier feature store catalog...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Online Lookup Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-white mb-2">⚡ Sub-Millisecond Online Feature Retrieval</h2>
        <p className="text-xs text-slate-400 mb-4">Query low-latency online Redis/In-Memory store by entity join key.</p>

        <div className="flex items-center gap-3 mb-4">
          <input 
            type="text"
            value={lookupKey}
            onChange={e => setLookupKey(e.target.value)}
            placeholder="Entity Key (e.g. u1001)"
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500 font-mono"
          />
          <button 
            onClick={handleLookup}
            className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-lg transition shadow-md shadow-teal-500/20"
          >
            Fetch Online Features
          </button>
        </div>

        {lookupResult && (
          <pre className="bg-slate-950 border border-slate-800 p-3 rounded-lg font-mono text-xs text-emerald-400 overflow-auto">
            {JSON.stringify(lookupResult, null, 2)}
          </pre>
        )}
      </div>

      {/* Feature Views Catalog */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-base font-bold text-white mb-4">Registered Feature Views</h2>
        <div className="space-y-4">
          {featureViews.map((fv: any) => (
            <div key={fv.name} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-teal-400">{fv.name}</span>
                <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400 font-mono">TTL: {fv.ttl_seconds}s</span>
              </div>
              <div className="text-xs text-slate-300">
                <span className="font-semibold text-slate-400">Entities: </span>
                {fv.entities.map((e: any) => `${e.name} (key=${e.join_key})`).join(', ')}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-400">Features:</span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2">
                  {fv.features.map((f: any) => (
                    <div key={f.name} className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg text-xs">
                      <div className="font-bold text-slate-200">{f.name}</div>
                      <div className="text-slate-500 font-mono text-[11px]">{f.data_type} • {f.feature_type}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
