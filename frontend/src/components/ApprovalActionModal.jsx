import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Send, 
  X, 
  Loader2,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { 
  submitDecisionForReview, 
  approveDecision, 
  rejectDecision, 
  escalateDecision 
} from '../api/approvals';

export const ApprovalActionModal = ({ 
  isOpen, 
  onClose, 
  decision, 
  currentLevel = 1,
  actionType = 'approve', // 'approve' | 'reject' | 'escalate' | 'submit'
  onSuccess 
}) => {
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen || !decision) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (actionType === 'submit') {
        await submitDecisionForReview(decision.id, { comments });
      } else if (actionType === 'approve') {
        await approveDecision(decision.id, { comments });
      } else if (actionType === 'reject') {
        if (!comments || comments.trim().length < 3) {
          setError('Rejection reason / feedback comments are mandatory (minimum 3 characters).');
          setLoading(false);
          return;
        }
        await rejectDecision(decision.id, comments);
      } else if (actionType === 'escalate') {
        await escalateDecision(decision.id, { reason: comments || 'Urgent SLA escalation' });
      }

      setComments('');
      onSuccess?.();
      onClose();
    } catch (err) {
      console.error('Workflow action failed:', err);
      setError(err.response?.data?.detail || 'Failed to complete workflow action.');
    } finally {
      setLoading(false);
    }
  };

  const getModalConfig = () => {
    switch (actionType) {
      case 'approve':
        return {
          title: `Approve Decision (Level ${currentLevel})`,
          subtitle: currentLevel === 1 
            ? 'Level 1 review pass will advance this decision to Level 2 Manager review.'
            : 'Final Level 2 approval will transition this decision to Approved status.',
          buttonText: `Confirm Level ${currentLevel} Approval`,
          buttonColor: 'bg-emerald-600 hover:bg-emerald-500',
          icon: <CheckCircle2 className="w-6 h-6 text-emerald-400" />,
          placeholder: 'Optional approval notes or architectural verification remarks...'
        };
      case 'reject':
        return {
          title: `Reject Decision (Level ${currentLevel})`,
          subtitle: 'Decision will be returned to Rejected status with mandatory feedback.',
          buttonText: 'Confirm Rejection',
          buttonColor: 'bg-rose-600 hover:bg-rose-500',
          icon: <XCircle className="w-6 h-6 text-rose-400" />,
          placeholder: 'Explain why this decision cannot be approved (required)...'
        };
      case 'escalate':
        return {
          title: 'Escalate Decision Review',
          subtitle: 'Elevate this decision to Senior Leadership / Manager queue for expedited resolution.',
          buttonText: 'Confirm Escalation',
          buttonColor: 'bg-amber-600 hover:bg-amber-500',
          icon: <AlertTriangle className="w-6 h-6 text-amber-400" />,
          placeholder: 'Reason for review escalation (e.g. Turnaround SLA breached)...'
        };
      case 'submit':
      default:
        return {
          title: 'Submit Decision for Review',
          subtitle: 'Initiates Level 1 multi-level approval pipeline and notifies assigned reviewer.',
          buttonText: 'Submit for Level 1 Review',
          buttonColor: 'bg-blue-600 hover:bg-blue-500',
          icon: <Send className="w-6 h-6 text-blue-400" />,
          placeholder: 'Submission comments or instructions for reviewer...'
        };
    }
  };

  const config = getModalConfig();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between gap-4">
          <div className="flex items-start space-x-3">
            <div className="p-2.5 rounded-2xl bg-slate-800 shrink-0">
              {config.icon}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">{config.title}</h2>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{config.subtitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Decision Summary Banner */}
        <div className="px-6 py-3 bg-slate-950/60 border-b border-slate-800/80 text-xs">
          <span className="text-slate-500 font-medium">Target Decision:</span>{' '}
          <span className="text-slate-200 font-semibold">{decision.title}</span>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
              <XCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5 tracking-wider">
              {actionType === 'reject' ? 'Rejection Feedback (Mandatory)' : 'Comments / Rationale'}
            </label>
            <textarea
              rows={4}
              required={actionType === 'reject'}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder={config.placeholder}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`px-5 py-2.5 rounded-xl text-white text-xs font-bold shadow-lg transition-all flex items-center space-x-2 ${config.buttonColor} disabled:opacity-50`}
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              <span>{config.buttonText}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApprovalActionModal;
