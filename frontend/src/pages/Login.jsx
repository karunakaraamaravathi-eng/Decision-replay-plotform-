import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Layers, Lock, Mail, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Authentication failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Quick fill helper for testing different roles easily
  const handleQuickLogin = (testEmail, testPassword) => {
    setEmail(testEmail);
    setPassword(testPassword);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 shadow-lg shadow-brand-500/25 mb-2">
            <Layers className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Welcome back
          </h1>
          <p className="text-sm text-slate-400">
            Sign in to access your decisions, reviews, and workflows
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 sm:p-8 shadow-xl backdrop-blur-xl">
          {error && (
            <div className="mb-6 flex items-center gap-3 rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-400">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium uppercase tracking-wider text-slate-400 mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@organization.com"
                  className="w-full rounded-lg border border-slate-800 bg-slate-950/70 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium uppercase tracking-wider text-slate-400">
                  Password
                </label>
              </div>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-slate-800 bg-slate-950/70 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand-600 to-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-md shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Pre-seeded Roles for Testing */}
          <div className="mt-6 pt-6 border-t border-slate-800/80">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-brand-400" />
              Quick Demo Accounts (1-Click Fill)
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@decisionreplay.com', 'Admin@123')}
                className="text-left px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-950/50 hover:bg-slate-800/60 hover:border-slate-700 transition-all text-xs"
              >
                <div className="font-medium text-rose-400">Admin</div>
                <div className="text-[11px] text-slate-500 truncate">admin@...</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('manager@decisionreplay.com', 'Manager@123')}
                className="text-left px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-950/50 hover:bg-slate-800/60 hover:border-slate-700 transition-all text-xs"
              >
                <div className="font-medium text-amber-400">Manager</div>
                <div className="text-[11px] text-slate-500 truncate">manager@...</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('reviewer@decisionreplay.com', 'Reviewer@123')}
                className="text-left px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-950/50 hover:bg-slate-800/60 hover:border-slate-700 transition-all text-xs"
              >
                <div className="font-medium text-indigo-400">Reviewer</div>
                <div className="text-[11px] text-slate-500 truncate">reviewer@...</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('employee@decisionreplay.com', 'Employee@123')}
                className="text-left px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-950/50 hover:bg-slate-800/60 hover:border-slate-700 transition-all text-xs"
              >
                <div className="font-medium text-emerald-400">Employee</div>
                <div className="text-[11px] text-slate-500 truncate">employee@...</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Link */}
        <p className="text-center text-sm text-slate-400">
          Don't have an account yet?{' '}
          <Link to="/register" className="font-medium text-brand-400 hover:text-brand-300 transition-colors">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
};
