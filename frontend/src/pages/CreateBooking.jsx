import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { bookingService } from '../services/bookingService';
import { venueService } from '../services/venueService';
import toast from 'react-hot-toast';

const CreateBooking = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const preSelectedVenue = location.state?.venue;

  const [venues, setVenues] = useState([]);
  const [formData, setFormData] = useState({
    venue: preSelectedVenue?.id || '',
    title: '',
    description: '',
    booking_date: '',
    start_time: '',
    end_time: '',
    priority: '5',
  });
  const [availability, setAvailability] = useState(null);
  const [checking, setChecking] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVenues();
  }, []);

  const loadVenues = async () => {
    try {
      const data = await venueService.getVenues();
      setVenues(data.results || data);
    } catch (error) {
      toast.error('Failed to load venues');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setAvailability(null);
  };

  const checkAvailability = async () => {
    if (!formData.venue || !formData.booking_date || !formData.start_time || !formData.end_time) {
      toast.error('Please fill in venue, date, and time fields');
      return;
    }

    setChecking(true);
    try {
      const result = await bookingService.checkAvailability({
        venue_id: formData.venue,
        date: formData.booking_date,
        start_time: formData.start_time,
        end_time: formData.end_time,
      });
      setAvailability(result);
      if (result.is_available) {
        toast.success('Slot is available!');
      } else {
        toast.error(result.reason || 'Slot is not available');
      }
    } catch (error) {
      toast.error('Failed to check availability');
    } finally {
      setChecking(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!availability || !availability.is_available) {
      toast.error('Please check slot availability first');
      return;
    }

    setLoading(true);
    try {
      const response = await bookingService.createBooking(formData);
      
      if (response.payment_required) {
        toast.success('Pre-booking created! Proceeding to payment...');
        // TODO: Integrate Razorpay payment
        navigate(`/bookings/${response.booking.id}`);
      } else {
        toast.success('Booking created and sent for approval!');
        navigate('/bookings');
      }
    } catch (error) {
      if (error.response?.status === 409) {
        toast.error('Slot conflict detected');
      } else {
        toast.error('Failed to create booking');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Create Booking</h1>

      <form onSubmit={handleSubmit} className="card space-y-6">
        {/* Venue Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Venue *
          </label>
          <select
            name="venue"
            required
            className="input-field"
            value={formData.venue}
            onChange={handleChange}
          >
            <option value="">Select a venue</option>
            {venues.map((venue) => (
              <option key={venue.id} value={venue.id}>
                {venue.name} ({venue.category_display})
              </option>
            ))}
          </select>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Event Title *
          </label>
          <input
            type="text"
            name="title"
            required
            className="input-field"
            placeholder="e.g., Tech Club Meeting"
            value={formData.title}
            onChange={handleChange}
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            name="description"
            rows="3"
            className="input-field"
            placeholder="Brief description of your event"
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        {/* Date and Time */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </label>
            <input
              type="date"
              name="booking_date"
              required
              className="input-field"
              value={formData.booking_date}
              onChange={handleChange}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Time *
            </label>
            <input
              type="time"
              name="start_time"
              required
              className="input-field"
              value={formData.start_time}
              onChange={handleChange}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Time *
            </label>
            <input
              type="time"
              name="end_time"
              required
              className="input-field"
              value={formData.end_time}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Priority Level *
          </label>
          <select
            name="priority"
            required
            className="input-field"
            value={formData.priority}
            onChange={handleChange}
          >
            <option value="5">Personal/Informal Use (P5)</option>
            <option value="4">Club/Cultural Event (P4)</option>
            <option value="3">Department/School Meet (P3)</option>
            <option value="2">Academic Event (P2)</option>
            <option value="1">Exam/University Event (P1)</option>
          </select>
        </div>

        {/* Availability Check */}
        <div className="border-t pt-6">
          <button
            type="button"
            onClick={checkAvailability}
            disabled={checking}
            className="btn-secondary w-full mb-4"
          >
            {checking ? 'Checking...' : 'Check Slot Availability'}
          </button>

          {availability && (
            <div
              className={`p-4 rounded-lg ${
                availability.is_available
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <p
                className={`font-medium ${
                  availability.is_available ? 'text-green-800' : 'text-red-800'
                }`}
              >
                {availability.is_available
                  ? '✓ Slot is available!'
                  : '✗ ' + (availability.reason || 'Slot is not available')}
              </p>
            </div>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !availability?.is_available}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? 'Creating Booking...' : 'Create Booking'}
        </button>
      </form>
    </div>
  );
};

export default CreateBooking;
