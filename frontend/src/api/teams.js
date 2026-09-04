import apiClient from './axios';

export const teamsApi = {
  getTeams: async () => {
    const response = await apiClient.get('/teams');
    return response.data;
  },

  createTeam: async (teamData) => {
    const response = await apiClient.post('/teams', teamData);
    return response.data;
  },

  getTeamById: async (teamId) => {
    const response = await apiClient.get(`/teams/${teamId}`);
    return response.data;
  },
};
