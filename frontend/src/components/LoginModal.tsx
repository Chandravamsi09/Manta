import React, { useState } from 'react';
import { apiFetch } from '../services/api.ts';
import { ShieldCheck, Lock, User, AlertCircle } from 'lucide-react';

interface LoginModalProps {
  onSuccess: (username: string) => void;
}

export default function LoginModal({ onSuccess }: LoginModalProps) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiFetch('/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      });
      localStorage.setItem('manta_token', res.data.token);
      localStorage.setItem('manta_user', res.data.username);
      onSuccess(res.data.username);
    } catch (err: any) {
      setError(err.message || 'Login failed. Check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950 z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-teal-500 flex items-center justify-center font-black text-slate-950 text-2xl shadow-lg shadow-teal-500/20">
            M
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Manta ML Systems</h2>
            <p className="text-xs text-teal-400">Enterprise Control Plane Authentication</p>
          </div>
        </div>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Username</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input 
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-teal-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password / API Key</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input 
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-teal-500"
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm rounded-lg transition shadow-md shadow-teal-500/20 disabled:opacity-50"
          >
            {isLoading ? 'Authenticating...' : 'Sign In to Dashboard'}
          </button>
        </form>

        <div className="text-xs text-slate-500 text-center border-t border-slate-800 pt-4">
          Demo Enterprise Credentials: <span className="text-teal-400 font-mono">admin / admin123</span>
        </div>
      </div>
    </div>
  );
}
