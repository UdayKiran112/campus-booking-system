import api from './api';

export const venueService = {
  getVenues: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/venues/?${params}`);
    return response.data;
  },

  getVenueById: async (id) => {
    const response = await api.get(`/venues/${id}/`);
    return response.data;
  },

  getVenueCategories: async () => {
    const response = await api.get('/venues/categories/');
    return response.data;
  },

  getVenueTypes: async (category = null) => {
    const params = category ? `?category=${category}` : '';
    const response = await api.get(`/venues/types/${params}`);
    return response.data;
  },

  getVenuePricing: async (venueId) => {
    const response = await api.get(`/venues/${venueId}/pricing/`);
    return response.data;
  },

  createVenue: async (venueData) => {
    const response = await api.post('/venues/create/', venueData);
    return response.data;
  },

  updateVenue: async (venueId, venueData) => {
    const response = await api.put(`/venues/${venueId}/update/`, venueData);
    return response.data;
  },

  blockVenue: async (venueId, blockData) => {
    const response = await api.post(`/venues/${venueId}/block/`, blockData);
    return response.data;
  },
};
