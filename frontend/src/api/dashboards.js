import api from './axios';

export const getEmployeeDashboard = async () => {
  const res = await api.get('/dashboards/employee');
  return res.data;
};

export const getManagerDashboard = async () => {
  const res = await api.get('/dashboards/manager');
  return res.data;
};

export const getAdminDashboard = async () => {
  const res = await api.get('/dashboards/admin');
  return res.data;
};
