import api from './api';

export const bookingService = {
  getBookings: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/bookings/?${params}`);
    return response.data;
  },

  getBookingById: async (id) => {
    const response = await api.get(`/bookings/${id}/`);
    return response.data;
  },

  createBooking: async (bookingData) => {
    const response = await api.post('/bookings/create/', bookingData);
    return response.data;
  },

  checkAvailability: async (slotData) => {
    const response = await api.post('/bookings/check-availability/', slotData);
    return response.data;
  },

  getAlternativeSlots: async (venueId, date, duration = 2) => {
    const response = await api.get(
      `/bookings/alternative-slots/${venueId}/?date=${date}&duration=${duration}`
    );
    return response.data;
  },

  approveBooking: async (bookingId) => {
    const response = await api.post(`/bookings/${bookingId}/approve/`);
    return response.data;
  },

  rejectBooking: async (bookingId, reason) => {
    const response = await api.post(`/bookings/${bookingId}/reject/`, { reason });
    return response.data;
  },

  confirmPayment: async (bookingId, paymentId) => {
    const response = await api.post(`/bookings/${bookingId}/confirm-payment/`, {
      payment_id: paymentId,
    });
    return response.data;
  },

  cancelBooking: async (bookingId, reason) => {
    const response = await api.post(`/bookings/${bookingId}/cancel/`, { reason });
    return response.data;
  },

  requestReview: async (bookingId) => {
    const response = await api.post(`/bookings/${bookingId}/request-review/`);
    return response.data;
  },
};
