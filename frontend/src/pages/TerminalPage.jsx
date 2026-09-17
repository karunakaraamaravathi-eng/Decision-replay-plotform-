import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { exportDecisionsReport, exportApprovalsReport, exportAuditReport } from '../api/reports';
import { Terminal, Shield, Play, ArrowRight, CornerDownLeft, Sparkles, HelpCircle, Trash2, Maximize2, Minimize2 } from 'lucide-react';

export const TerminalPage = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Initial welcome banner
    setHistory([
      {
        type: 'banner',
        content: `
================================================================================
   EXPERT DECISION REPLAY PLATFORM  //  INTERACTIVE GOVERNANCE CLI v3.0
================================================================================
 [SYSTEM STATUS: ONLINE]   [ENVIRONMENT: LOCAL DEV]   [AUTH ROLE: ${user?.role || 'ANONYMOUS'}]
 Connected as: ${user?.full_name || 'User'} <${user?.email || 'unknown'}>

 Type 'help' for a full list of commands or 'workflow --help' for approval actions.
--------------------------------------------------------------------------------`
      }
    ]);
  }, [user]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  const handleCommand = async (e) => {
    e.preventDefault();
    const rawCmd = input.trim();
    if (!rawCmd) return;

    // Add to history
    setCommandHistory((prev) => [rawCmd, ...prev]);
    setHistoryIndex(-1);
    setInput('');

    const newEntries = [{ type: 'command', cmd: rawCmd }];
    setHistory((prev) => [...prev, ...newEntries]);

    const parts = rawCmd.split(/\s+/);
    const mainCmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    setLoading(true);

    try {
      switch (mainCmd) {
        case 'clear':
        case 'cls':
          setHistory([]);
          setLoading(false);
          return;

        case 'help':
          setHistory((prev) => [
            ...prev,
            {
              type: 'help',
              content: [
                { cmd: 'help', desc: 'Display all available system commands' },
                { cmd: 'whoami', desc: 'Display active user credentials, role, and permissions' },
                { cmd: 'status', desc: 'Check backend API and platform health status' },
                { cmd: 'decisions [list]', desc: 'List active architectural decisions & their approval tiers' },
                { cmd: 'decisions get <id>', desc: 'Inspect full details and alternatives for decision <id>' },
                { cmd: 'workflow submit <id>', desc: 'Submit a draft decision to Level 1 Reviewer queue' },
                { cmd: 'workflow approve <id> [notes]', desc: 'Approve decision at current verification tier' },
                { cmd: 'workflow reject <id> <reason>', desc: 'Reject decision with mandatory rationale' },
                { cmd: 'workflow escalate <id> <reason>', desc: 'Escalate decision with governance urgency flag' },
                { cmd: 'workflow history <id>', desc: 'View chronological approval audit trail for decision' },
                { cmd: 'audit [tail <n>]', desc: 'Stream latest audit compliance entries (Admin/Manager)' },
                { cmd: 'notifications [list|read-all]', desc: 'View or mark in-app alert notifications' },
                { cmd: 'stats', desc: 'Fetch role-specific dashboard metrics' },
                { cmd: 'export <decisions|approvals|audit> <pdf|excel>', desc: 'Generate and trigger download of enterprise report' },
                { cmd: 'clear / cls', desc: 'Clear the terminal output screen' }
              ]
            }
          ]);
          break;

        case 'whoami':
          setHistory((prev) => [
            ...prev,
            {
              type: 'output',
              content: `User ID:    #${user?.id}
Name:       ${user?.full_name}
Email:      ${user?.email}
Role:       ${user?.role}
Session:    Active (JWT Bearer)`
            }
          ]);
          break;

        case 'status':
          const healthRes = await api.get('/health');
          setHistory((prev) => [
            ...prev,
            {
              type: 'success',
              content: `Backend Status: ${healthRes.data?.status || 'OK'}\nService: ${healthRes.data?.service || 'Decision Platform'}\nVersion: ${healthRes.data?.version || '1.0.0'}\nDatabase: Connected (SQLite / Local)`
            }
          ]);
          break;

        case 'decisions':
          if (args[0] === 'get' && args[1]) {
            const decId = parseInt(args[1], 10);
            const res = await api.get(`/decisions/${decId}`);
            const d = res.data;
            setHistory((prev) => [
              ...prev,
              {
                type: 'output',
                content: `--------------------------------------------------------
DECISION #${d.id}: ${d.title}
--------------------------------------------------------
Status:          ${d.status} (Level ${d.current_approval_level || 1})
Category:        ${d.category}
Author:          ${d.creator?.full_name || `User #${d.created_by_id}`}
Created:         ${new Date(d.created_at).toLocaleString()}
Alternatives:    ${d.alternatives?.length || 0} evaluated
Approvals:       ${d.approvals?.length || 0} records
Comments:        ${d.comments?.length || 0} entries

PROBLEM STATEMENT:
${d.problem_statement}`
              }
            ]);
          } else {
            const res = await api.get('/decisions/');
            const list = res.data;
            if (!list || list.length === 0) {
              setHistory((prev) => [...prev, { type: 'info', content: 'No decisions found in system.' }]);
            } else {
              const formatted = list.map((d) => 
                `[#${String(d.id).padEnd(3)}] ${d.title.padEnd(35).substring(0, 35)} | ${d.status.padEnd(13)} | Level ${d.current_approval_level || 1} | ${d.category}`
              ).join('\n');
              setHistory((prev) => [
                ...prev,
                {
                  type: 'output',
                  content: `ID     TITLE                               | STATUS        | LEVEL   | CATEGORY\n--------------------------------------------------------------------------------\n${formatted}`
                }
              ]);
            }
          }
          break;

        case 'workflow':
          const subAction = args[0]?.toLowerCase();
          const targetId = parseInt(args[1], 10);

          if (!targetId || isNaN(targetId)) {
            setHistory((prev) => [
              ...prev,
              {
                type: 'error',
                content: `Usage: workflow <submit|approve|reject|escalate|history> <decision_id> [arguments]`
              }
            ]);
            break;
          }

          if (subAction === 'submit') {
            await api.post(`/decisions/${targetId}/submit-for-review`);
            setHistory((prev) => [
              ...prev,
              {
                type: 'success',
                content: `[SUCCESS] Decision #${targetId} submitted for review. Advanced to Level 1 Reviewer queue.`
              }
            ]);
          } else if (subAction === 'approve') {
            const comments = args.slice(2).join(' ') || 'Approved via Governance CLI';
            const res = await api.post(`/decisions/${targetId}/approve`, { comments });
            setHistory((prev) => [
              ...prev,
              {
                type: 'success',
                content: `[SUCCESS] Decision #${targetId} approved at Level ${res.data?.level}.\nOutcome: Decision status is now "${res.data?.decision_status}".`
              }
            ]);
          } else if (subAction === 'reject') {
            const reason = args.slice(2).join(' ');
            if (!reason) {
              setHistory((prev) => [
                ...prev,
                { type: 'error', content: `[ERROR] Rejection requires a mandatory reason.\nExample: workflow reject ${targetId} Insufficient benchmark metrics` }
              ]);
              break;
            }
            const res = await api.post(`/decisions/${targetId}/reject`, { comments: reason });
            setHistory((prev) => [
              ...prev,
              {
                type: 'warning',
                content: `[REJECTED] Decision #${targetId} has been rejected.\nRationale: "${reason}". Status is now "${res.data?.decision_status}".`
              }
            ]);
          } else if (subAction === 'escalate') {
            const reason = args.slice(2).join(' ');
            if (!reason) {
              setHistory((prev) => [
                ...prev,
                { type: 'error', content: `[ERROR] Escalation requires a mandatory reason.\nExample: workflow escalate ${targetId} Production SLA timeout` }
              ]);
              break;
            }
            const res = await api.post(`/decisions/${targetId}/escalate`, { comments: reason });
            setHistory((prev) => [
              ...prev,
              {
                type: 'warning',
                content: `[ESCALATED] Decision #${targetId} escalated.\nReason: "${reason}". Level: ${res.data?.level}.`
              }
            ]);
          } else if (subAction === 'history') {
            const res = await api.get(`/decisions/${targetId}/approval-history`);
            const histList = res.data;
            if (!histList || histList.length === 0) {
              setHistory((prev) => [...prev, { type: 'info', content: `No approval history on record for Decision #${targetId}.` }]);
            } else {
              const formatted = histList.map((h) => 
                `[${new Date(h.created_at).toLocaleTimeString()}] ${h.action.padEnd(10)} | Level ${h.level} | By ${h.approver?.full_name || 'System'}: "${h.comments || 'N/A'}"`
              ).join('\n');
              setHistory((prev) => [
                ...prev,
                {
                  type: 'output',
                  content: `HISTORICAL APPROVAL TRAIL FOR DECISION #${targetId}:\n--------------------------------------------------------------------------------\n${formatted}`
                }
              ]);
            }
          } else {
            setHistory((prev) => [
              ...prev,
              { type: 'error', content: `Unknown workflow action '${subAction}'. Valid options: submit, approve, reject, escalate, history.` }
            ]);
          }
          break;

        case 'audit':
          const limit = parseInt(args[1], 10) || 10;
          const auditRes = await api.get('/audit/', { params: { limit } });
          const logs = auditRes.data;
          if (!logs || logs.length === 0) {
            setHistory((prev) => [...prev, { type: 'info', content: 'No audit records found.' }]);
          } else {
            const formatted = logs.map((l) => 
              `[${new Date(l.timestamp).toLocaleTimeString()}] ${l.action.padEnd(8)} | ${l.resource_type.padEnd(10)} #${String(l.resource_id).padEnd(4)} | User #${l.user_id} (${l.ip_address || '127.0.0.1'})`
            ).join('\n');
            setHistory((prev) => [
              ...prev,
              {
                type: 'output',
                content: `LATEST ${logs.length} AUDIT LOG EVENTS:\n--------------------------------------------------------------------------------\n${formatted}`
              }
            ]);
          }
          break;

        case 'notifications':
          if (args[0] === 'read-all') {
            await api.post('/notifications/mark-all-read');
            setHistory((prev) => [...prev, { type: 'success', content: '[SUCCESS] All notifications marked as read.' }]);
          } else {
            const notifRes = await api.get('/notifications/');
            const notifs = notifRes.data;
            if (!notifs || notifs.length === 0) {
              setHistory((prev) => [...prev, { type: 'info', content: 'No notifications found.' }]);
            } else {
              const formatted = notifs.map((n) => 
                `[${n.is_read ? 'READ' : 'NEW '}] ${n.title} | ${n.message} (${new Date(n.created_at).toLocaleTimeString()})`
              ).join('\n');
              setHistory((prev) => [
                ...prev,
                {
                  type: 'output',
                  content: `NOTIFICATION ALERTS (${notifs.length}):\n--------------------------------------------------------------------------------\n${formatted}`
                }
              ]);
            }
          }
          break;

        case 'stats':
          const role = user?.role?.toLowerCase() || 'employee';
          let endpoint = '/dashboards/employee';
          if (role === 'administrator') endpoint = '/dashboards/admin';
          else if (role === 'manager') endpoint = '/dashboards/manager';

          const dashRes = await api.get(endpoint);
          const data = dashRes.data;
          setHistory((prev) => [
            ...prev,
            {
              type: 'output',
              content: `DASHBOARD METRICS [${role.toUpperCase()}]:\n${JSON.stringify(data, null, 2)}`
            }
          ]);
          break;

        case 'export':
          const targetReport = args[0]?.toLowerCase();
          const format = args[1]?.toLowerCase() || 'pdf';

          if (!['pdf', 'excel'].includes(format)) {
            setHistory((prev) => [...prev, { type: 'error', content: 'Format must be either "pdf" or "excel".' }]);
            break;
          }

          if (targetReport === 'decisions') {
            await exportDecisionsReport(format);
            setHistory((prev) => [...prev, { type: 'success', content: `[EXPORT COMPLETE] Decisions Summary report downloaded as ${format.toUpperCase()}.` }]);
          } else if (targetReport === 'approvals') {
            await exportApprovalsReport(format);
            setHistory((prev) => [...prev, { type: 'success', content: `[EXPORT COMPLETE] Approvals SLA report downloaded as ${format.toUpperCase()}.` }]);
          } else if (targetReport === 'audit') {
            await exportAuditReport(format);
            setHistory((prev) => [...prev, { type: 'success', content: `[EXPORT COMPLETE] Audit Compliance report downloaded as ${format.toUpperCase()}.` }]);
          } else {
            setHistory((prev) => [...prev, { type: 'error', content: 'Unknown report type. Usage: export <decisions|approvals|audit> <pdf|excel>' }]);
          }
          break;

        default:
          setHistory((prev) => [
            ...prev,
            {
              type: 'error',
              content: `Command not recognized: '${mainCmd}'. Type 'help' to see available commands.`
            }
          ]);
          break;
      }
    } catch (err) {
      console.error('CLI execution error:', err);
      const msg = err.response?.data?.detail || err.message || 'Execution error';
      setHistory((prev) => [
        ...prev,
        { type: 'error', content: `[EXECUTION ERROR]: ${msg}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const nextIdx = Math.min(historyIndex + 1, commandHistory.length - 1);
        setHistoryIndex(nextIdx);
        setInput(commandHistory[nextIdx]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const nextIdx = historyIndex - 1;
        setHistoryIndex(nextIdx);
        setInput(commandHistory[nextIdx]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white flex items-center space-x-2">
              <span>Platform Governance Console</span>
              <span className="text-xs font-mono font-normal px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                CLI v3.0
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Interactive terminal interface for executing approval workflows, querying audit logs, and running reports.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setHistory([])}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-bold border border-slate-800 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear Screen</span>
          </button>
        </div>
      </div>

      {/* Terminal Window Box */}
      <div 
        onClick={focusInput}
        className="glass-card rounded-3xl border border-slate-800 shadow-2xl overflow-hidden bg-slate-950/95 font-mono text-xs cursor-text flex flex-col min-h-[580px]"
      >
        {/* Window Chrome */}
        <div className="px-5 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between select-none">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
            <span className="text-slate-400 text-[11px] font-semibold ml-2">
              replay-governance-sh • {user?.role || 'User'}
            </span>
          </div>
          <div className="text-[10px] text-slate-500">
            Press &uarr; &darr; for history • Type 'help' for manual
          </div>
        </div>

        {/* Terminal Screen Body */}
        <div className="p-6 flex-1 space-y-4 overflow-y-auto max-h-[620px]">
          {history.map((entry, idx) => (
            <div key={idx} className="space-y-1">
              {entry.type === 'banner' && (
                <pre className="text-emerald-400 whitespace-pre-wrap leading-relaxed">{entry.content}</pre>
              )}

              {entry.type === 'command' && (
                <div className="flex items-center space-x-2 text-white">
                  <span className="text-emerald-400 font-bold">➜</span>
                  <span className="text-blue-400 font-bold">~</span>
                  <span className="text-slate-100 font-semibold">{entry.cmd}</span>
                </div>
              )}

              {entry.type === 'output' && (
                <pre className="text-slate-300 pl-4 whitespace-pre-wrap leading-relaxed border-l-2 border-slate-800">{entry.content}</pre>
              )}

              {entry.type === 'success' && (
                <div className="pl-4 text-emerald-400 whitespace-pre-wrap border-l-2 border-emerald-500/50">
                  {entry.content}
                </div>
              )}

              {entry.type === 'warning' && (
                <div className="pl-4 text-amber-400 whitespace-pre-wrap border-l-2 border-amber-500/50">
                  {entry.content}
                </div>
              )}

              {entry.type === 'error' && (
                <div className="pl-4 text-rose-400 whitespace-pre-wrap border-l-2 border-rose-500/50">
                  {entry.content}
                </div>
              )}

              {entry.type === 'info' && (
                <div className="pl-4 text-slate-400 italic border-l-2 border-slate-800">
                  {entry.content}
                </div>
              )}

              {entry.type === 'help' && (
                <div className="pl-4 space-y-1 border-l-2 border-indigo-500/40 py-1">
                  <div className="text-indigo-300 font-bold mb-2">PLATFORM COMMAND DIRECTORY:</div>
                  {entry.content.map((item, i) => (
                    <div key={i} className="flex flex-col sm:flex-row sm:items-center text-slate-300">
                      <span className="w-56 font-bold text-emerald-400 font-mono">{item.cmd}</span>
                      <span className="text-slate-400 text-[11px]">{item.desc}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-2 text-blue-400 pl-4">
              <span className="animate-spin text-xs">⠋</span>
              <span className="text-xs">Executing command...</span>
            </div>
          )}

          {/* Active Input Line */}
          <form onSubmit={handleCommand} className="flex items-center space-x-2 pt-2">
            <span className="text-emerald-400 font-bold">➜</span>
            <span className="text-blue-400 font-bold">~</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type command here (e.g. 'help', 'decisions', 'stats')..."
              className="flex-1 bg-transparent text-slate-100 placeholder-slate-600 focus:outline-none font-mono text-xs"
              autoFocus
            />
            <button type="submit" className="text-slate-500 hover:text-slate-300">
              <CornerDownLeft className="w-3.5 h-3.5" />
            </button>
          </form>

          <div ref={bottomRef} />
        </div>
      </div>

    </div>
  );
};

export default TerminalPage;
