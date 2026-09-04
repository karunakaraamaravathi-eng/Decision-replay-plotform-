import React, { useState, useEffect } from 'react';
import { usersApi } from '../api/users';
import { teamsApi } from '../api/teams';
import { RoleBadge } from '../components/RoleBadge';
import {
  Users,
  Shield,
  Search,
  Building2,
  CheckCircle,
  XCircle,
  Plus,
  RefreshCw,
  AlertCircle,
  UserCheck,
  UserX,
} from 'lucide-react';

export const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('');

  // Team creation modal / state
  const [newTeamName, setNewTeamName] = useState('');
  const [newTeamDesc, setNewTeamDesc] = useState('');
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [teamLoading, setTeamLoading] = useState(false);

  const fetchUsersAndTeams = async () => {
    setLoading(true);
    setError('');
    try {
      const [usersData, teamsData] = await Promise.all([
        usersApi.getUsers({ search: searchTerm || undefined, role: selectedRole || undefined }),
        teamsApi.getTeams(),
      ]);
      setUsers(usersData);
      setTeams(teamsData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load organizational users.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsersAndTeams();
  }, [selectedRole]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchUsersAndTeams();
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await usersApi.updateUserRole(userId, newRole);
      setSuccessMsg(`Role successfully updated to ${newRole}`);
      setTimeout(() => setSuccessMsg(''), 4000);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user role.');
      setTimeout(() => setError(''), 4000);
    }
  };

  const handleStatusToggle = async (userId, currentStatus) => {
    try {
      const newStatus = !currentStatus;
      await usersApi.toggleUserStatus(userId, newStatus);
      setSuccessMsg(`User status changed to ${newStatus ? 'Active' : 'Disabled'}`);
      setTimeout(() => setSuccessMsg(''), 4000);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: newStatus } : u))
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle status.');
      setTimeout(() => setError(''), 4000);
    }
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    if (!newTeamName.trim()) return;
    setTeamLoading(true);
    try {
      const created = await teamsApi.createTeam({
        name: newTeamName.trim(),
        description: newTeamDesc.trim() || null,
      });
      setTeams((prev) => [...prev, created]);
      setNewTeamName('');
      setNewTeamDesc('');
      setShowTeamModal(false);
      setSuccessMsg(`Team "${created.name}" created successfully!`);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create team.');
    } finally {
      setTeamLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">
                User & Role Administration
              </h1>
              <p className="text-xs text-slate-400">
                Manage organizational access, roles (RBAC), and team assignments
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowTeamModal(true)}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-all shadow-sm"
          >
            <Plus className="h-4 w-4 text-brand-400" />
            New Team
          </button>

          <button
            onClick={fetchUsersAndTeams}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-brand-400' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-xs font-medium text-emerald-300">
          <CheckCircle className="h-4 w-4 text-emerald-400" />
          {successMsg}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-medium text-rose-400">
          <AlertCircle className="h-4 w-4 text-rose-400" />
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Search className="h-4 w-4 text-slate-500" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search users by name or email..."
            className="w-full rounded-lg border border-slate-800 bg-slate-950/70 py-2 pl-9 pr-4 text-xs text-slate-100 placeholder-slate-500 focus:border-brand-500 focus:outline-none"
          />
        </form>

        <div className="flex items-center gap-2">
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-950/70 py-2 px-3 text-xs text-slate-200 focus:border-brand-500 focus:outline-none"
          >
            <option value="">All Roles</option>
            <option value="ADMINISTRATOR">Administrator</option>
            <option value="MANAGER">Manager</option>
            <option value="REVIEWER">Reviewer</option>
            <option value="EMPLOYEE">Employee</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800 text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-semibold uppercase tracking-wider">
              <tr>
                <th scope="col" className="px-6 py-3.5">User</th>
                <th scope="col" className="px-6 py-3.5">Team</th>
                <th scope="col" className="px-6 py-3.5">Current Role</th>
                <th scope="col" className="px-6 py-3.5">Role Assignment</th>
                <th scope="col" className="px-6 py-3.5">Status</th>
                <th scope="col" className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-2">
                      <div className="h-6 w-6 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
                      <span>Loading user directory...</span>
                    </div>
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                    No users found matching your criteria.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-200">{u.full_name}</div>
                      <div className="text-slate-400 text-[11px]">{u.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      {u.team ? (
                        <span className="inline-flex items-center gap-1 text-slate-300 font-medium">
                          <Building2 className="h-3.5 w-3.5 text-slate-500" />
                          {u.team.name}
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">None</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <RoleBadge role={u.role} size="sm" />
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-200 focus:border-brand-500 focus:outline-none"
                      >
                        <option value="EMPLOYEE">Employee</option>
                        <option value="REVIEWER">Reviewer</option>
                        <option value="MANAGER">Manager</option>
                        <option value="ADMINISTRATOR">Administrator</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] text-rose-400">
                          <span className="h-1.5 w-1.5 rounded-full bg-rose-400" />
                          Disabled
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleStatusToggle(u.id, u.is_active)}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                          u.is_active
                            ? 'text-rose-400 hover:bg-rose-500/10'
                            : 'text-emerald-400 hover:bg-emerald-500/10'
                        }`}
                      >
                        {u.is_active ? (
                          <>
                            <UserX className="h-3.5 w-3.5" />
                            Deactivate
                          </>
                        ) : (
                          <>
                            <UserCheck className="h-3.5 w-3.5" />
                            Activate
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Team Modal */}
      {showTeamModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-base font-semibold text-white">Create New Team</h2>
              <button
                onClick={() => setShowTeamModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Team Name</label>
                <input
                  type="text"
                  required
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="e.g. Cloud Infrastructure Group"
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Description (Optional)</label>
                <textarea
                  rows={3}
                  value={newTeamDesc}
                  onChange={(e) => setNewTeamDesc(e.target.value)}
                  placeholder="Scope of decisions and organizational focus..."
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-brand-500 focus:outline-none resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTeamModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={teamLoading}
                  className="px-4 py-1.5 rounded-lg bg-brand-600 text-xs font-semibold text-white hover:bg-brand-500 disabled:opacity-50"
                >
                  {teamLoading ? 'Creating...' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
