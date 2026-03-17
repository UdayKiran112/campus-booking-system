import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { bookingService } from '../services/bookingService';
import { venueService } from '../services/venueService';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    upcomingBookings: 0,
    pendingApprovals: 0,
    totalVenues: 0,
  });
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [bookingsRes, venuesRes] = await Promise.all([
        bookingService.getBookings({ status: 'CONFIRMED,PENDING_APPROVAL' }),
        venueService.getVenues(),
      ]);

      const bookings = bookingsRes.results || bookingsRes;
      const venues = venuesRes.results || venuesRes;

      setStats({
        upcomingBookings: bookings.filter(b => b.status === 'CONFIRMED').length,
        pendingApprovals: bookings.filter(b => b.status === 'PENDING_APPROVAL').length,
        totalVenues: venues.length,
      });

      setRecentBookings(bookings.slice(0, 5));
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      CONFIRMED: 'badge-confirmed',
      PENDING_APPROVAL: 'badge-pending',
      APPROVED: 'badge-approved',
      REJECTED: 'badge-rejected',
    };
    return badges[status] || 'badge-pending';
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {user?.first_name}!
        </h1>
        <p className="text-gray-600 mt-1">Here's what's happening with your bookings</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Upcoming Bookings</h3>
          <p className="text-3xl font-bold text-primary-600 mt-2">{stats.upcomingBookings}</p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Pending Approvals</h3>
          <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.pendingApprovals}</p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Available Venues</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">{stats.totalVenues}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/venues" className="btn-primary text-center">
            Search Venues
          </Link>
          <Link to="/bookings/create" className="btn-primary text-center">
            Create Booking
          </Link>
          <Link to="/bookings" className="btn-secondary text-center">
            View My Bookings
          </Link>
        </div>
      </div>

      {/* Recent Bookings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Bookings</h2>
        {recentBookings.length === 0 ? (
          <p className="text-gray-500">No bookings yet. Create your first booking!</p>
        ) : (
          <div className="space-y-3">
            {recentBookings.map((booking) => (
              <div key={booking.id} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50">
                <div>
                  <h3 className="font-medium">{booking.title}</h3>
                  <p className="text-sm text-gray-600">
                    {booking.venue_details?.name} • {booking.booking_date} • {booking.start_time}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={getStatusBadge(booking.status)}>
                    {booking.status_display}
                  </span>
                  <Link to={`/bookings/${booking.id}`} className="text-primary-600 hover:text-primary-700">
                    View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
