import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { RoleBadge } from '../components/RoleBadge';
import { usersApi } from '../api/users';
import {
  User,
  Mail,
  Building2,
  Calendar,
  CheckCircle2,
  ShieldAlert,
  ArrowUpRight,
  FileText,
  Clock,
  BarChart3,
  Users,
  Settings,
  Sparkles,
  Award,
} from 'lucide-react';

export const Dashboard = () => {
  const { user, refreshUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saveLoading, setSaveLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setSaveLoading(true);
    setMessage('');
    try {
      await usersApi.updateProfile(user.id, { full_name: fullName });
      await refreshUser();
      setMessage('Profile updated successfully!');
      setEditing(false);
    } catch (err) {
      setMessage('Failed to update profile.');
    } finally {
      setSaveLoading(false);
    }
  };

  const getRoleCapabilities = () => {
    switch (user?.role) {
      case 'ADMINISTRATOR':
        return [
          'Full organizational user and role assignment management',
          'System governance, team structuring, and security audit logs',
          'Platform-wide decision catalog administration and analytics',
        ];
      case 'MANAGER':
        return [
          'Team-level decision oversight and priority evaluation',
          'Approval workflow multi-stage sign-offs',
          'Team analytics, velocity reports, and alternative comparisons',
        ];
      case 'REVIEWER':
        return [
          'In-depth alternative analysis, feasibility & risk reviews',
          'Approval queue evaluation and discussion feedback threads',
          'Technical validation of recorded decision rationale',
        ];
      case 'EMPLOYEE':
      default:
        return [
          'Record new organizational decisions and alternatives',
          'Participate in discussion threads and document rationale',
          'Explore institutional knowledge repository and search history',
        ];
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900/90 to-brand-950/40 p-6 sm:p-8 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
                Welcome back, {user?.full_name}
              </h1>
              <RoleBadge role={user?.role} />
            </div>
            <p className="text-sm text-slate-400 max-w-2xl">
              Expert Decision Replay Platform &bull; Milestone 1: Secure Authentication & Role-Based Access Control
            </p>
          </div>

          <div className="flex items-center gap-3">
            {user?.role === 'ADMINISTRATOR' && (
              <Link
                to="/admin/users"
                className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-500/20 hover:bg-brand-500 transition-all"
              >
                <Users className="h-4 w-4" />
                Manage Users & Roles
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Grid: Profile Card & Role Privileges */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <User className="h-5 w-5 text-brand-400" />
              <h2 className="text-base font-semibold text-white">Profile Overview</h2>
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="text-xs font-medium text-brand-400 hover:text-brand-300"
            >
              {editing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          {message && (
            <div className="p-3 text-xs rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              {message}
            </div>
          )}

          {editing ? (
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-brand-500 focus:outline-none"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={saveLoading}
                className="w-full rounded-lg bg-brand-600 py-2 text-xs font-semibold text-white hover:bg-brand-500 transition-colors"
              >
                {saveLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          ) : (
            <div className="space-y-4 text-sm">
              <div className="flex items-center justify-between py-1">
                <span className="text-slate-400 flex items-center gap-2">
                  <Mail className="h-4 w-4 text-slate-500" /> Email
                </span>
                <span className="font-medium text-slate-200">{user?.email}</span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-slate-400 flex items-center gap-2">
                  <Award className="h-4 w-4 text-slate-500" /> Current Role
                </span>
                <RoleBadge role={user?.role} size="sm" />
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-slate-400 flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-slate-500" /> Assigned Team
                </span>
                <span className="font-medium text-slate-200">
                  {user?.team ? user.team.name : 'Unassigned'}
                </span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-slate-400 flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" /> Status
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-slate-400 flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-slate-500" /> Member Since
                </span>
                <span className="text-xs text-slate-400">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Today'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Role Privileges & Capabilities */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl space-y-6">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-800">
            <Sparkles className="h-5 w-5 text-amber-400" />
            <h2 className="text-base font-semibold text-white">
              {user?.role} Privileges & Capabilities
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {getRoleCapabilities().map((cap, idx) => (
              <div
                key={idx}
                className="flex flex-col justify-between rounded-xl border border-slate-800/80 bg-slate-950/60 p-4 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-start gap-2.5">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-500/10 text-brand-400 text-xs font-bold mt-0.5">
                    {idx + 1}
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed">{cap}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Milestone 1 Verified Status */}
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-emerald-300">
                  Milestone 1 Completed (Weeks 1-2)
                </h3>
                <p className="text-xs text-emerald-400/80 mt-1">
                  Database models (Users, Teams, Roles), FastAPI RBAC endpoints, JWT security, and React Router protected routing are fully operational.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Role-Specific Workspaces Preview (Milestones 2-4 Roadmap) */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white tracking-tight">
          Module Workspaces & Fast Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 hover:border-brand-500/40 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
                <FileText className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                Milestone 2
              </span>
            </div>
            <h3 className="text-sm font-semibold text-white">Decision Management</h3>
            <p className="text-xs text-slate-400 mt-1">
              Document problem statements, categories, and decision status.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 hover:border-brand-500/40 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
                <BarChart3 className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                Milestone 2
              </span>
            </div>
            <h3 className="text-sm font-semibold text-white">Alternative Analysis</h3>
            <p className="text-xs text-slate-400 mt-1">
              Compare pros/cons, cost, feasibility, and risk assessments.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 hover:border-brand-500/40 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
                <Clock className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                Milestone 3
              </span>
            </div>
            <h3 className="text-sm font-semibold text-white">Approval Workflows</h3>
            <p className="text-xs text-slate-400 mt-1">
              Multi-level approval queues and reviewer delegation.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 hover:border-brand-500/40 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-400">
                <Users className="h-5 w-5" />
              </div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Active (M1)
              </span>
            </div>
            <h3 className="text-sm font-semibold text-white">User & Role Management</h3>
            <p className="text-xs text-slate-400 mt-1">
              RBAC permissions, team rosters, and access policies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
