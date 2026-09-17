import api from './axios';

export const triggerBlobDownload = (data, filename) => {
  const url = window.URL.createObjectURL(new Blob([data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const exportDecisionsReport = async (format = 'pdf', decisionId = null) => {
  const res = await api.get('/reports/decisions/export', {
    params: { format, decision_id: decisionId },
    responseType: 'blob'
  });
  const ext = format === 'pdf' ? 'pdf' : 'xlsx';
  const filename = `decisions_report_${new Date().toISOString().slice(0,10)}.${ext}`;
  triggerBlobDownload(res.data, filename);
};

export const exportSingleDecisionReport = async (id, format = 'pdf') => {
  const res = await api.get(`/reports/decisions/${id}/export`, {
    params: { format },
    responseType: 'blob'
  });
  const ext = format === 'pdf' ? 'pdf' : 'xlsx';
  const filename = `decision_${id}_dossier.${ext}`;
  triggerBlobDownload(res.data, filename);
};

export const exportApprovalsReport = async (format = 'pdf') => {
  const res = await api.get('/reports/approvals/export', {
    params: { format },
    responseType: 'blob'
  });
  const ext = format === 'pdf' ? 'pdf' : 'xlsx';
  const filename = `approvals_turnaround_report.${ext}`;
  triggerBlobDownload(res.data, filename);
};

export const exportAuditReport = async (format = 'pdf') => {
  const res = await api.get('/reports/audit/export', {
    params: { format },
    responseType: 'blob'
  });
  const ext = format === 'pdf' ? 'pdf' : 'xlsx';
  const filename = `audit_compliance_report.${ext}`;
  triggerBlobDownload(res.data, filename);
};
