import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  FileBarChart, 
  FileText, 
  Download, 
  ShieldCheck, 
  Clock, 
  Layers, 
  Calendar, 
  FileSpreadsheet, 
  Loader2,
  CheckCircle2,
  AlertCircle,
  Filter
} from 'lucide-react';
import { 
  exportDecisionsReport, 
  exportApprovalsReport, 
  exportAuditReport 
} from '../api/reports';

export const ReportsPage = () => {
  const { user, isAdmin, isManager } = useAuth();
  const [downloading, setDownloading] = useState(null); // 'decisions-pdf' | 'decisions-excel' | ...
  const [successMsg, setSuccessMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleExport = async (type, format) => {
    const key = `${type}-${format}`;
    setDownloading(key);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (type === 'decisions') {
        await exportDecisionsReport(format);
      } else if (type === 'approvals') {
        await exportApprovalsReport(format);
      } else if (type === 'audit') {
        await exportAuditReport(format);
      }
      setSuccessMsg(`Successfully generated and downloaded ${format.toUpperCase()} report.`);
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err) {
      console.error('Export failed:', err);
      setErrorMsg(err.response?.data?.detail || `Failed to export ${type} report.`);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="glass-card rounded-3xl p-8 border border-slate-800 relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-950/30">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400">
              <FileBarChart className="w-3.5 h-3.5" />
              <span>Milestone 3 Reporting & Compliance Engine</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white">
              Enterprise Reports & Data Exports
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              Generate auditable, production-grade PDF dossiers and multi-sheet Excel workbooks for organizational decision histories, approval turnaround SLAs, and regulatory compliance logs.
            </p>
          </div>
        </div>
      </div>

      {/* Notifications / Alerts */}
      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center space-x-3">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* REPORT CARD 1: DECISION SUMMARY REPORT */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between hover:border-blue-500/40 transition-all group space-y-6">
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
              <Layers className="w-6 h-6" />
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-blue-400">
                Core Knowledge
              </span>
              <h2 className="text-lg font-bold text-white mt-1">Decision Summary Dossier</h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Comprehensive archive of organizational decisions including problem statements, evaluated alternatives with cost/feasibility matrices, pros/cons, and the complete multi-level approval trail.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
              <p>• Multi-tab workbook layout (Summary & Alternatives)</p>
              <p>• Formatted decision metadata and version tracking</p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => handleExport('decisions', 'pdf')}
              disabled={downloading !== null}
              className="flex-1 py-2.5 px-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 text-xs font-bold transition-all border border-rose-500/30 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {downloading === 'decisions-pdf' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileText className="w-4 h-4" />
              )}
              <span>Export PDF</span>
            </button>

            <button
              onClick={() => handleExport('decisions', 'excel')}
              disabled={downloading !== null}
              className="flex-1 py-2.5 px-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-bold transition-all border border-emerald-500/30 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {downloading === 'decisions-excel' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileSpreadsheet className="w-4 h-4" />
              )}
              <span>Export Excel</span>
            </button>
          </div>
        </div>

        {/* REPORT CARD 2: APPROVAL TURNAROUND REPORT */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between hover:border-amber-500/40 transition-all group space-y-6">
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400">
                Governance & SLA
              </span>
              <h2 className="text-lg font-bold text-white mt-1">Approval Turnaround & Team Velocity</h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Tracks multi-level reviewer velocity, queue latency, turnaround time by approval level (Level 1 vs Level 2), and rejection rates to monitor operational productivity.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
              <p>• SLA threshold tracking and turnaround analytics</p>
              <p>• Approver audit trail with reviewer feedback</p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => handleExport('approvals', 'pdf')}
              disabled={downloading !== null}
              className="flex-1 py-2.5 px-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 text-xs font-bold transition-all border border-rose-500/30 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {downloading === 'approvals-pdf' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileText className="w-4 h-4" />
              )}
              <span>Export PDF</span>
            </button>

            <button
              onClick={() => handleExport('approvals', 'excel')}
              disabled={downloading !== null}
              className="flex-1 py-2.5 px-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-bold transition-all border border-emerald-500/30 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {downloading === 'approvals-excel' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileSpreadsheet className="w-4 h-4" />
              )}
              <span>Export Excel</span>
            </button>
          </div>
        </div>

        {/* REPORT CARD 3: AUDIT TRAIL & COMPLIANCE (ADMIN & MANAGER) */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between hover:border-purple-500/40 transition-all group space-y-6">
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold tracking-wider text-purple-400">
                  Compliance & Security
                </span>
                <span className="text-[10px] font-semibold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                  Admin / Manager
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mt-1">Audit Trail & Compliance Log</h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Immutable chronological log capturing user modifications, status transitions, IP addresses, authentication security events, and granular resource diffs for regulatory compliance.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
              <p>• ISO 27001 and enterprise security compliant</p>
              <p>• Detailed user action logs and IP address history</p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => handleExport('audit', 'pdf')}
              disabled={downloading !== null || (!isAdmin && !isManager)}
              className="flex-1 py-2.5 px-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 text-xs font-bold transition-all border border-rose-500/30 flex items-center justify-center space-x-2 disabled:opacity-40"
              title={!isAdmin && !isManager ? 'Restricted to Manager and Admin' : ''}
            >
              {downloading === 'audit-pdf' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileText className="w-4 h-4" />
              )}
              <span>Export PDF</span>
            </button>

            <button
              onClick={() => handleExport('audit', 'excel')}
              disabled={downloading !== null || (!isAdmin && !isManager)}
              className="flex-1 py-2.5 px-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 text-xs font-bold transition-all border border-emerald-500/30 flex items-center justify-center space-x-2 disabled:opacity-40"
              title={!isAdmin && !isManager ? 'Restricted to Manager and Admin' : ''}
            >
              {downloading === 'audit-excel' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileSpreadsheet className="w-4 h-4" />
              )}
              <span>Export Excel</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ReportsPage;
