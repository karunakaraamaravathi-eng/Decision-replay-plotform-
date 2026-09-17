import api from './axios';

export const submitDecisionForReview = async (decisionId, payload = {}) => {
  const res = await api.post(`/decisions/${decisionId}/submit-for-review`, payload);
  return res.data;
};

export const approveDecision = async (decisionId, payload = {}) => {
  const res = await api.post(`/decisions/${decisionId}/approve`, payload);
  return res.data;
};

export const rejectDecision = async (decisionId, comments) => {
  const res = await api.post(`/decisions/${decisionId}/reject`, { comments });
  return res.data;
};

export const escalateDecision = async (decisionId, payload = {}) => {
  const res = await api.post(`/decisions/${decisionId}/escalate`, payload);
  return res.data;
};

export const getApprovalHistory = async (decisionId) => {
  const res = await api.get(`/decisions/${decisionId}/approval-history`);
  return res.data;
};
