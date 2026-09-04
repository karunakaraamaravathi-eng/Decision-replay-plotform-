import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { RoleBadge } from '../components/RoleBadge';

export const Unauthorized = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-2xl backdrop-blur-xl">
        <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20 shadow-lg">
          <ShieldAlert className="h-8 w-8" />
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Access Restricted</h1>
          <p className="text-xs text-slate-400 leading-relaxed">
            Your current role does not have authorization to view this administrative resource.
          </p>
        </div>

        {user && (
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 text-xs flex items-center justify-between">
            <span className="text-slate-400">Your Current Role:</span>
            <RoleBadge role={user.role} size="sm" />
          </div>
        )}

        <div className="pt-2">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 px-5 py-2.5 text-xs font-semibold transition-all border border-slate-700"
          >
            <ArrowLeft className="h-4 w-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};
