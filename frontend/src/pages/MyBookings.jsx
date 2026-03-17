import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { bookingService } from '../services/bookingService';
import toast from 'react-hot-toast';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookings();
  }, [filter]);

  const loadBookings = async () => {
    setLoading(true);
    try {
      const filters = filter !== 'all' ? { status: filter } : {};
      const data = await bookingService.getBookings(filters);
      setBookings(data.results || data);
    } catch (error) {
      toast.error('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      PRE_BOOKED: 'badge-pending',
      PENDING_APPROVAL: 'badge-pending',
      APPROVED: 'badge-approved',
      CONFIRMED: 'badge-confirmed',
      REJECTED: 'badge-rejected',
      CANCELLED: 'bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium',
    };
    return badges[status] || 'badge-pending';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Bookings</h1>
        <Link to="/bookings/create" className="btn-primary">Create New Booking</Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['all', 'PENDING_APPROVAL', 'CONFIRMED', 'APPROVED', 'REJECTED', 'CANCELLED'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
              filter === status
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {status === 'all' ? 'All' : status.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Bookings List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : bookings.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No bookings found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold">{booking.title}</h3>
                    <span className={getStatusBadge(booking.status)}>
                      {booking.status_display}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p><span className="font-medium">Venue:</span> {booking.venue_details?.name}</p>
                    <p><span className="font-medium">Date:</span> {booking.booking_date}</p>
                    <p><span className="font-medium">Time:</span> {booking.start_time} - {booking.end_time}</p>
                    <p><span className="font-medium">Reference:</span> {booking.booking_reference}</p>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  <Link
                    to={`/bookings/${booking.id}`}
                    className="btn-primary text-center whitespace-nowrap"
                  >
                    View Details
                  </Link>
                  {booking.status === 'PRE_BOOKED' && (
                    <button className="btn-secondary text-center whitespace-nowrap">
                      Complete Payment
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyBookings;
