import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', { username, password });
    if (response.data.user) {
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async () => {
    await api.post('/auth/logout/');
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me/');
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/profile/update/', profileData);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  changePassword: async (passwordData) => {
    const response = await api.post('/auth/change-password/', passwordData);
    return response.data;
  },

  getStoredUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};
