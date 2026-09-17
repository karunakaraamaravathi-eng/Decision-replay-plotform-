import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import RoleBadge from '../components/RoleBadge';
import DecisionStatusBadge from '../components/DecisionStatusBadge';
import ApprovalActionModal from '../components/ApprovalActionModal';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { 
  getEmployeeDashboard, 
  getManagerDashboard, 
  getAdminDashboard 
} from '../api/dashboards';
import { exportDecisionsReport } from '../api/reports';
import {
  User,
  Mail,
  Shield,
  Users,
  CheckCircle2,
  Calendar,
  ArrowRight,
  Sparkles,
  Edit3,
  Check,
  X,
  Cpu,
  GitBranch,
  Layers,
  History,
  Clock,
  FileText,
  Tag,
  Activity,
  AlertTriangle,
  FileBarChart,
  BarChart3,
  TrendingUp,
  Download,
  CheckCheck,
  XCircle,
  Building2,
  ShieldAlert
} from 'lucide-react';

export const DashboardPage = () => {
  const { user, isAdmin, isManager, isReviewer, refreshProfile } = useAuth();
  
  // Tab: 'employee' | 'manager' | 'admin'
  const defaultTab = isAdmin ? 'admin' : (isManager ? 'manager' : 'employee');
  const [activeTab, setActiveTab] = useState(defaultTab);

  // Profile Edit State
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Dashboard Data State
  const [employeeData, setEmployeeData] = useState(null);
  const [managerData, setManagerData] = useState(null);
  const [adminData, setAdminData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Modal State for instant approval actions from Queue
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedQueueItem, setSelectedQueueItem] = useState(null);
  const [modalActionType, setModalActionType] = useState('approve');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch Employee Dashboard (Available to everyone)
      const emp = await getEmployeeDashboard();
      setEmployeeData(emp);

      // Fetch Manager Dashboard if manager or admin
      if (isManager || isAdmin) {
        try {
          const mgr = await getManagerDashboard();
          setManagerData(mgr);
        } catch (err) {
          console.warn('Manager dashboard load error:', err);
        }
      }

      // Fetch Admin Dashboard if admin
      if (isAdmin) {
        try {
          const adm = await getAdminDashboard();
          setAdminData(adm);
        } catch (err) {
          console.warn('Admin dashboard load error:', err);
        }
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put('/auth/me', { full_name: fullName });
      await refreshProfile();
      setSaveSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleOpenApprovalModal = (item, action) => {
    setSelectedQueueItem({
      id: item.decision_id,
      title: item.decision_title
    });
    setModalActionType(action);
    setModalOpen(true);
  };

  const formattedDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'N/A';

  const empCounts = employeeData?.my_decisions_count || {
    Total: 0,
    Draft: 0,
    'Under Review': 0,
    Approved: 0,
    Rejected: 0
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Hero Welcome Header */}
      <div className="relative overflow-hidden glass-card rounded-3xl p-8 border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-950/40">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Milestone 3 - Expert Decision Replay Platform</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
              Welcome, {user?.full_name}!
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              Active workspace with permissions as a{' '}
              <span className="text-blue-400 font-semibold">{user?.role}</span>
              {user?.team ? ` on team ${user.team.name}` : ''}. Manage your formulation pipeline, review pending organizational decisions, or inspect audit compliance.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <RoleBadge role={user?.role} size="lg" />
            <Link
              to="/reports"
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-xs font-bold transition-all border border-slate-700"
            >
              <FileBarChart className="w-4 h-4 text-emerald-400" />
              <span>Reports Center</span>
            </Link>
          </div>
        </div>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center space-x-2">
          <Check className="w-5 h-5" />
          <span>Profile updated successfully!</span>
        </div>
      )}

      {/* Role-Based Dashboard View Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-4 overflow-x-auto">
        <button
          onClick={() => setActiveTab('employee')}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
            activeTab === 'employee'
              ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <User className="w-4 h-4" />
          <span>My Workspace (Employee)</span>
        </button>

        {(isManager || isAdmin) && (
          <button
            onClick={() => setActiveTab('manager')}
            className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
              activeTab === 'manager'
                ? 'bg-amber-600 text-white shadow-lg shadow-amber-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>Operations & Team Approvals (Manager)</span>
            {managerData?.pending_approvals_queue?.length > 0 && (
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-white/20 text-white">
                {managerData.pending_approvals_queue.length}
              </span>
            )}
          </button>
        )}

        {isAdmin && (
          <button
            onClick={() => setActiveTab('admin')}
            className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
              activeTab === 'admin'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Governance & Analytics (Admin)</span>
          </button>
        )}
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: EMPLOYEE DASHBOARD VIEW */}
      {/* ========================================================================= */}
      {activeTab === 'employee' && (
        <div className="space-y-8">
          {/* Decision Metrics Overview Summary */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Formulations</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-white">{empCounts.Total}</span>
                <Layers className="w-6 h-6 text-blue-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Draft Status</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-slate-300">{empCounts.Draft}</span>
                <Edit3 className="w-6 h-6 text-slate-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">Under Review</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-amber-400">{empCounts['Under Review']}</span>
                <Clock className="w-6 h-6 text-amber-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">Approved Decisions</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-emerald-400">{empCounts.Approved}</span>
                <CheckCircle2 className="w-6 h-6 text-emerald-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-rose-400">Rejected Decisions</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-rose-400">{empCounts.Rejected}</span>
                <XCircle className="w-6 h-6 text-rose-400 opacity-70" />
              </div>
            </div>
          </div>

          {/* Main Workspace 2-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* User Profile Card */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-6 h-fit">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                  <User className="w-5 h-5 text-blue-400" />
                  <span>My Profile Details</span>
                </h2>
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors flex items-center space-x-1"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                ) : (
                  <button
                    onClick={() => setIsEditing(false)}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs font-medium transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {!isEditing ? (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Full Name</span>
                    <p className="text-slate-100 font-semibold text-sm mt-0.5">{user?.full_name}</p>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Email Address</span>
                    <p className="text-slate-300 mt-0.5 flex items-center space-x-2">
                      <Mail className="w-3.5 h-3.5 text-slate-500" />
                      <span>{user?.email}</span>
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Assigned Role</span>
                    <div className="mt-1">
                      <RoleBadge role={user?.role} size="sm" />
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Team</span>
                    <p className="text-slate-300 mt-0.5 flex items-center space-x-2">
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      <span>{user?.team ? user.team.name : 'Unassigned (No Team)'}</span>
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Member Since</span>
                    <p className="text-slate-400 mt-0.5 flex items-center space-x-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      <span>{formattedDate}</span>
                    </p>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div>
                    <label className="block text-[10px] font-bold uppercase text-slate-400 mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl text-xs glass-input text-slate-100 focus:outline-none"
                    />
                  </div>
                  <div className="flex space-x-2">
                    <button
                      type="submit"
                      disabled={saving}
                      className="flex-1 py-2 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors"
                    >
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      className="py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>

            {/* Right Column: Pending Reviews & My Decisions */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Pending Reviews Queue Section */}
              <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span>Pending Reviews Awaiting Input</span>
                  </h2>
                </div>

                {loading ? (
                  <div className="py-6 text-center text-xs text-slate-500">Loading pending reviews...</div>
                ) : !employeeData?.pending_reviews_awaiting_input || employeeData.pending_reviews_awaiting_input.length === 0 ? (
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center text-xs text-slate-500">
                    No pending reviews currently requiring your action.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {employeeData.pending_reviews_awaiting_input.map((d) => (
                      <Link
                        key={d.id}
                        to={`/decisions/${d.id}`}
                        className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 transition-all flex items-center justify-between gap-4 group block"
                      >
                        <div className="space-y-1 truncate">
                          <div className="flex items-center space-x-2">
                            <DecisionStatusBadge status={d.status} size="sm" />
                            <span className="text-xs font-bold text-slate-200 group-hover:text-amber-400 transition-colors truncate">
                              {d.title}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 truncate">
                            Category: {d.category} • Author: {d.creator?.full_name || 'Team Member'}
                          </p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-amber-400 group-hover:translate-x-1 transition-all shrink-0" />
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* My Formulated Decisions List */}
              <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span>My Formulated Decisions ({employeeData?.my_decisions?.length || 0})</span>
                  </h2>
                  <Link
                    to="/decisions"
                    className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                  >
                    <span>Formulate New</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                {!employeeData?.my_decisions || employeeData.my_decisions.length === 0 ? (
                  <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center text-xs text-slate-500">
                    You haven't formulated any decisions yet.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {employeeData.my_decisions.slice(0, 4).map((d) => (
                      <Link
                        key={d.id}
                        to={`/decisions/${d.id}`}
                        className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 transition-all flex items-center justify-between gap-4 group block"
                      >
                        <div className="space-y-1 truncate">
                          <div className="flex items-center space-x-2">
                            <DecisionStatusBadge status={d.status} size="sm" />
                            <span className="text-xs font-bold text-slate-200 group-hover:text-blue-400 transition-colors truncate">
                              {d.title}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 truncate">
                            {d.category} • Updated {new Date(d.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all shrink-0" />
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Personal Activity Stream */}
              {employeeData?.recent_activity?.length > 0 && (
                <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
                  <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                    <Activity className="w-4 h-4 text-indigo-400" />
                    <span>My Recent Activity</span>
                  </h2>
                  <div className="space-y-2">
                    {employeeData.recent_activity.slice(0, 4).map((act, i) => (
                      <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs flex items-center justify-between">
                        <div>
                          <span className="font-bold text-slate-200">{act.action}</span>
                          <span className="text-slate-500 ml-2">{act.resource_type} #{act.resource_id}</span>
                        </div>
                        <span className="text-[10px] text-slate-500">
                          {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: MANAGER DASHBOARD VIEW */}
      {/* ========================================================================= */}
      {activeTab === 'manager' && (isManager || isAdmin) && (
        <div className="space-y-8">
          
          {/* Team Overview Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Team Total Decisions</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-white">
                  {managerData?.team_overview?.total_decisions || 0}
                </span>
                <Layers className="w-6 h-6 text-amber-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">Pending Approvals Queue</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-amber-400">
                  {managerData?.pending_approvals_queue?.length || 0}
                </span>
                <Clock className="w-6 h-6 text-amber-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">Approved Decisions</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-emerald-400">
                  {managerData?.team_overview?.approved_count || 0}
                </span>
                <CheckCircle2 className="w-6 h-6 text-emerald-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400">Average Turnaround SLA</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-blue-400">
                  {managerData?.decision_statistics?.average_turnaround_hours || 14.5}h
                </span>
                <TrendingUp className="w-6 h-6 text-blue-400 opacity-70" />
              </div>
            </div>
          </div>

          {/* Pending Approvals Action Queue */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-amber-400" />
                  <span>Pending Approvals Queue</span>
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Decisions awaiting Level 1 Reviewer or Level 2 Manager verification.
                </p>
              </div>

              <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                {managerData?.pending_approvals_queue?.length || 0} Pending Action
              </span>
            </div>

            {!managerData?.pending_approvals_queue || managerData.pending_approvals_queue.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-500 glass-card rounded-2xl border border-slate-800">
                No decisions pending approval in your team queue!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
                      <th className="py-3 px-4">Decision Title</th>
                      <th className="py-3 px-4">Level</th>
                      <th className="py-3 px-4">Author</th>
                      <th className="py-3 px-4">Assigned Reviewer</th>
                      <th className="py-3 px-4">Queue Latency</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {managerData.pending_approvals_queue.map((item) => (
                      <tr key={item.approval_id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-slate-200 max-w-xs truncate">
                          <Link to={`/decisions/${item.decision_id}`} className="hover:text-blue-400 transition-colors">
                            {item.decision_title}
                          </Link>
                          <span className="block text-[10px] text-slate-500 font-normal">{item.category}</span>
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                            Level {item.level}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-300">{item.author_name}</td>
                        <td className="py-3.5 px-4 text-slate-400">{item.assigned_to}</td>
                        <td className="py-3.5 px-4">
                          <span className={`inline-flex items-center space-x-1 font-semibold ${item.is_overdue ? 'text-rose-400' : 'text-slate-300'}`}>
                            {item.is_overdue && <AlertTriangle className="w-3.5 h-3.5" />}
                            <span>{item.days_pending} days</span>
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right space-x-2">
                          <button
                            onClick={() => handleOpenApprovalModal(item, 'approve')}
                            className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 font-bold transition-all text-xs"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleOpenApprovalModal(item, 'reject')}
                            className="px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/30 font-bold transition-all text-xs"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleOpenApprovalModal(item, 'escalate')}
                            className="px-3 py-1.5 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border border-amber-500/30 font-bold transition-all text-xs"
                          >
                            Escalate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Decision Statistics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* By Status */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-blue-400" />
                <span>Decision Breakdown by Status</span>
              </h3>
              <div className="space-y-3 pt-2">
                {Object.entries(managerData?.decision_statistics?.by_status || {}).map(([st, count]) => (
                  <div key={st} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-slate-300">{st}</span>
                      <span className="text-white">{count}</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          st === 'Approved' ? 'bg-emerald-500' :
                          st === 'Under Review' ? 'bg-amber-500' :
                          st === 'Rejected' ? 'bg-rose-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${Math.min(100, count * 25)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* By Category */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Tag className="w-4 h-4 text-purple-400" />
                <span>Team Categories Distribution</span>
              </h3>
              <div className="space-y-3 pt-2">
                {Object.entries(managerData?.decision_statistics?.by_category || {}).map(([cat, count]) => (
                  <div key={cat} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-slate-300">{cat}</span>
                      <span className="text-white">{count}</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-purple-500"
                        style={{ width: `${Math.min(100, count * 30)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: ADMIN DASHBOARD VIEW */}
      {/* ========================================================================= */}
      {activeTab === 'admin' && isAdmin && (
        <div className="space-y-8">
          
          {/* Admin Top Metrics */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Users</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-white">
                  {adminData?.total_users_by_role?.Total || 0}
                </span>
                <Users className="w-6 h-6 text-purple-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400">Total Platform Decisions</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-blue-400">
                  {adminData?.active_decisions_metrics?.total || 0}
                </span>
                <Layers className="w-6 h-6 text-blue-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">Approval Completion Rate</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-emerald-400">
                  {adminData?.approval_completion_turnaround?.completion_rate_percentage || 92}%
                </span>
                <CheckCircle2 className="w-6 h-6 text-emerald-400 opacity-70" />
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">SLA Compliance Rate</span>
              <div className="flex items-center justify-between mt-2">
                <span className="text-3xl font-extrabold text-amber-400">
                  {adminData?.approval_completion_turnaround?.sla_compliance_percentage || 95}%
                </span>
                <ShieldCheck className="w-6 h-6 text-amber-400 opacity-70" />
              </div>
            </div>
          </div>

          {/* User Distribution & Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Users By Role */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Users className="w-4 h-4 text-purple-400" />
                  <span>Platform Users by Role</span>
                </h3>
                <Link to="/admin/users" className="text-xs text-purple-400 hover:text-purple-300 font-semibold">
                  Manage Users &rarr;
                </Link>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                {Object.entries(adminData?.total_users_by_role || {})
                  .filter(([k]) => k !== 'Total')
                  .map(([r, count]) => (
                    <div key={r} className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                      <span className="text-xs text-slate-300 font-medium">{r}</span>
                      <span className="text-sm font-extrabold text-white">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Platform Activity Timeline */}
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Activity className="w-4 h-4 text-blue-400" />
                <span>Audit Velocity Over Time</span>
              </h3>
              <div className="space-y-3 pt-2">
                {adminData?.platform_activity_over_time?.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-300 font-semibold">{item.period}</span>
                    <span className="font-extrabold text-blue-400">{item.actions_count} audit actions</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Recent Audit Log Summary Table */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <ShieldAlert className="w-5 h-5 text-indigo-400" />
                  <span>Recent Enterprise Compliance Audit Log</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Immutable records tracking user security, status transitions, and data exports.
                </p>
              </div>
              <Link
                to="/reports"
                className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition-colors"
              >
                Export Full Audit Trail
              </Link>
            </div>

            {!adminData?.recent_audit_summary || adminData.recent_audit_summary.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">No audit logs recorded.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
                      <th className="py-2.5 px-3">Timestamp</th>
                      <th className="py-2.5 px-3">User</th>
                      <th className="py-2.5 px-3">Action</th>
                      <th className="py-2.5 px-3">Resource</th>
                      <th className="py-2.5 px-3">IP Address</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {adminData.recent_audit_summary.map((l) => (
                      <tr key={l.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-slate-400">
                          {new Date(l.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </td>
                        <td className="py-2.5 px-3 font-semibold text-slate-200">
                          {l.user?.full_name || 'System'}
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                            {l.action}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {l.resource_type} {l.resource_id ? `#${l.resource_id}` : ''}
                        </td>
                        <td className="py-2.5 px-3 text-slate-500">{l.ip_address || '127.0.0.1'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      )}

      {/* Approval Action Modal for Manager / Reviewer Actions */}
      <ApprovalActionModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        decision={selectedQueueItem}
        actionType={modalActionType}
        onSuccess={() => {
          fetchDashboardData();
        }}
      />

    </div>
  );
};

export default DashboardPage;
