import React from 'react';
import { Database, Zap } from 'lucide-react';

export default function FeatureCatalog() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h2 className="text-lg font-semibold mb-4">Dual-Tier Feature Store Catalog</h2>
      <div className="space-y-3">
        <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-teal-400">user_features_v1</span>
            <span className="text-xs text-slate-400">Online Store: Redis (0.3ms)</span>
          </div>
          <p className="text-xs text-slate-400 mb-2">Features: click_through_rate, purchase_count_30d, account_age_days</p>
        </div>
      </div>
    </div>
  );
}
