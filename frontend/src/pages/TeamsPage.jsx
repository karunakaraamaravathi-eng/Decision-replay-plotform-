import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import RoleBadge from '../components/RoleBadge';
import { 
  Users2, 
  Plus, 
  CheckCircle2, 
  AlertCircle, 
  Calendar, 
  Search, 
  Mail, 
  ShieldCheck, 
  Layers, 
  UserCheck,
  ChevronDown,
  ChevronUp,
  Sparkles
} from 'lucide-react';

export const TeamsPage = () => {
  const { isManager, isAdmin } = useAuth();
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Expanded team members state
  const [expandedTeams, setExpandedTeams] = useState({});

  // Create Team Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const res = await api.get('/teams');
      setTeams(res.data);
      // Auto-expand all teams by default
      const exp = {};
      res.data.forEach((t) => { exp[t.id] = true; });
      setExpandedTeams(exp);
    } catch (err) {
      console.error("Failed to load teams:", err);
      setError("Failed to fetch teams.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const toggleExpand = (teamId) => {
    setExpandedTeams((prev) => ({ ...prev, [teamId]: !prev[teamId] }));
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError('');
    try {
      const res = await api.post('/teams', { name, description });
      setTeams((prev) => [...prev, { ...res.data, users: [] }]);
      setName('');
      setDescription('');
      setIsModalOpen(false);
      setSuccessMsg(`Team "${res.data.name}" created successfully!`);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      console.error("Failed to create team:", err);
      setError(err.response?.data?.detail || "Failed to create team.");
    } finally {
      setCreating(false);
    }
  };

  // Filtered teams
  const filteredTeams = teams.filter((t) => {
    const q = searchQuery.toLowerCase();
    const matchesTeam = t.name.toLowerCase().includes(q) || (t.description || '').toLowerCase().includes(q);
    const matchesMember = (t.users || []).some(
      (u) => u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || (u.role || '').toLowerCase().includes(q)
    );
    return matchesTeam || matchesMember;
  });

  const totalMembers = teams.reduce((acc, t) => acc + (t.users?.length || 0), 0);

  const getInitials = (name) => {
    if (!name) return '??';
    return name
      .split(' ')
      .map((part) => part[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header & Metric Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-2">
            <Users2 className="w-3.5 h-3.5" />
            <span>Organization Hierarchy & Engineering Roster</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Teams & Leadership</h1>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Explore dedicated technical squads, decision-making committees, and cross-functional architects driving platform decisions.
          </p>
        </div>

        {(isManager || isAdmin) && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-600/20 transition-all shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Create New Team</span>
          </button>
        )}
      </div>

      {/* Stats Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Teams</span>
            <div className="text-2xl font-extrabold text-white mt-1">{teams.length}</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Active Members</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1">{totalMembers}</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <UserCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Governance Tier</span>
            <div className="text-2xl font-extrabold text-blue-400 mt-1">Multi-Level</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search teams, members, roles, or emails..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs glass-input text-slate-100 placeholder-slate-500 focus:outline-none"
          />
        </div>

        <span className="text-xs text-slate-400 font-medium">
          Showing {filteredTeams.length} of {teams.length} teams
        </span>
      </div>

      {/* Success Banner */}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center space-x-2">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Teams Grid */}
      {loading ? (
        <div className="py-24 text-center text-slate-500">
          <div className="w-8 h-8 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mx-auto mb-3"></div>
          <span className="text-sm">Loading organizational directory...</span>
        </div>
      ) : filteredTeams.length === 0 ? (
        <div className="glass-card p-12 text-center rounded-3xl border border-slate-800 space-y-3">
          <Users2 className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-slate-300">No matching teams or members found</h3>
          <p className="text-slate-500 text-xs">
            Try adjusting your search criteria or create a new team using the button above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {filteredTeams.map((team) => {
            const isExpanded = expandedTeams[team.id] ?? true;
            const members = team.users || [];
            const isCoreTeam = team.name.includes("Core Architecture");

            return (
              <div
                key={team.id}
                className={`glass-card rounded-3xl p-6 border flex flex-col justify-between transition-all duration-300 ${
                  isCoreTeam
                    ? 'border-indigo-500/40 bg-gradient-to-br from-slate-900/90 via-indigo-950/20 to-slate-900/90 shadow-xl shadow-indigo-950/20'
                    : 'border-slate-800/90 hover:border-slate-700'
                }`}
              >
                <div className="space-y-4">
                  {/* Team Card Header */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center space-x-3.5">
                      <div
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-base shrink-0 shadow-lg ${
                          isCoreTeam
                            ? 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-indigo-500/30 ring-2 ring-indigo-400/30'
                            : 'bg-slate-800 text-slate-300 border border-slate-700'
                        }`}
                      >
                        <Users2 className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-base font-extrabold text-white tracking-tight">{team.name}</h3>
                          {isCoreTeam && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center space-x-1">
                              <Sparkles className="w-3 h-3" />
                              <span>Leadership</span>
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-400 font-medium">
                          {members.length} {members.length === 1 ? 'member' : 'assigned members'}
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleExpand(team.id)}
                      className="p-2 rounded-xl bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                      title={isExpanded ? "Collapse member roster" : "Expand member roster"}
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Team Description */}
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {team.description || 'Enterprise functional unit governing system proposals and implementations.'}
                  </p>

                  {/* Member Roster Section */}
                  {isExpanded && (
                    <div className="pt-3 border-t border-slate-800/80 space-y-3">
                      <div className="flex items-center justify-between text-[11px] uppercase font-bold tracking-wider text-slate-400">
                        <span>Team Roster</span>
                        <span className="text-indigo-400 font-extrabold">{members.length} Active</span>
                      </div>

                      {members.length === 0 ? (
                        <p className="text-xs text-slate-600 italic py-2">
                          No engineers assigned to this team yet.
                        </p>
                      ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {members.map((member) => (
                            <div
                              key={member.id}
                              className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800/80 hover:border-slate-700/80 transition-all flex items-start space-x-3"
                            >
                              <div className="w-8 h-8 rounded-xl bg-slate-800 text-blue-400 border border-blue-500/20 flex items-center justify-center font-extrabold text-[11px] shrink-0 mt-0.5">
                                {getInitials(member.full_name)}
                              </div>

                              <div className="min-w-0 flex-1 space-y-1">
                                <div className="flex items-center justify-between gap-1">
                                  <span className="font-bold text-slate-200 text-xs truncate">
                                    {member.full_name}
                                  </span>
                                </div>

                                <div className="flex items-center justify-between">
                                  <RoleBadge role={member.role} />
                                </div>

                                <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 truncate">
                                  <Mail className="w-3 h-3 text-slate-500 shrink-0" />
                                  <span className="truncate">{member.email}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Footer */}
                <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                  <span className="flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-600" />
                    <span>Established {new Date(team.created_at).toLocaleDateString()}</span>
                  </span>
                  <span className="font-semibold text-slate-400 text-[11px]">Squad #{team.id}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Team Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-card max-w-md w-full p-6 rounded-3xl border border-slate-800 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-100">Create New Team</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                  Team Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Data Analytics & AI"
                  className="w-full px-3.5 py-2.5 rounded-xl text-sm glass-input text-slate-100 placeholder-slate-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief summary of team objectives..."
                  className="w-full px-3.5 py-2.5 rounded-xl text-sm glass-input text-slate-100 placeholder-slate-500 focus:outline-none"
                ></textarea>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-600/20 disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default TeamsPage;
