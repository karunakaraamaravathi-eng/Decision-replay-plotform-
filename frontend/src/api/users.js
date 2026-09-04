import apiClient from './axios';

export const usersApi = {
  getUsers: async (params = {}) => {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },

  getUserById: async (userId) => {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  },

  updateProfile: async (userId, data) => {
    const response = await apiClient.put(`/users/${userId}`, data);
    return response.data;
  },

  updateUserRole: async (userId, role) => {
    const response = await apiClient.put(`/users/${userId}/role`, { role });
    return response.data;
  },

  toggleUserStatus: async (userId, isActive) => {
    const response = await apiClient.put(`/users/${userId}/status`, { is_active: isActive });
    return response.data;
  },
};
