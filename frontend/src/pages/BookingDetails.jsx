import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { bookingService } from '../services/bookingService';
import toast from 'react-hot-toast';

const BookingDetails = () => {
  const { id } = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBooking();
  }, [id]);

  const loadBooking = async () => {
    try {
      const data = await bookingService.getBookingById(id);
      setBooking(data);
    } catch (error) {
      toast.error('Failed to load booking details');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    
    try {
      await bookingService.cancelBooking(id, 'Cancelled by user');
      toast.success('Booking cancelled successfully');
      loadBooking();
    } catch (error) {
      toast.error('Failed to cancel booking');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  if (!booking) {
    return <div className="card text-center py-12"><p className="text-gray-500">Booking not found</p></div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Booking Details</h1>
      
      <div className="card">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-semibold">{booking.title}</h2>
            <p className="text-gray-600 mt-1">Reference: {booking.booking_reference}</p>
          </div>
          <span className={`px-4 py-2 rounded-full font-medium ${
            booking.status === 'CONFIRMED' ? 'bg-blue-100 text-blue-800' :
            booking.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
            booking.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {booking.status_display}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-3">Event Details</h3>
            <div className="space-y-2 text-sm">
              <p><span className="text-gray-600">Venue:</span> <span className="font-medium">{booking.venue_details?.name}</span></p>
              <p><span className="text-gray-600">Date:</span> <span className="font-medium">{booking.booking_date}</span></p>
              <p><span className="text-gray-600">Time:</span> <span className="font-medium">{booking.start_time} - {booking.end_time}</span></p>
              <p><span className="text-gray-600">Duration:</span> <span className="font-medium">{booking.duration_hours} hours</span></p>
              <p><span className="text-gray-600">Priority:</span> <span className="font-medium">{booking.priority_display}</span></p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Payment Information</h3>
            <div className="space-y-2 text-sm">
              <p><span className="text-gray-600">Payment Required:</span> <span className="font-medium">{booking.payment_required ? 'Yes' : 'No'}</span></p>
              {booking.payment_amount > 0 && (
                <p><span className="text-gray-600">Amount:</span> <span className="font-medium">₹{booking.payment_amount}</span></p>
              )}
              {booking.security_deposit > 0 && (
                <p><span className="text-gray-600">Security Deposit:</span> <span className="font-medium">₹{booking.security_deposit}</span></p>
              )}
              <p><span className="text-gray-600">Payment Status:</span> <span className="font-medium">{booking.payment_status}</span></p>
            </div>
          </div>
        </div>

        {booking.description && (
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-gray-700">{booking.description}</p>
          </div>
        )}

        {booking.rejection_reason && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">Rejection Reason</h3>
            <p className="text-red-700">{booking.rejection_reason}</p>
          </div>
        )}

        <div className="mt-6 flex gap-3">
          {booking.status === 'PRE_BOOKED' && (
            <button className="btn-primary">Complete Payment</button>
          )}
          {['PRE_BOOKED', 'PENDING_APPROVAL', 'APPROVED'].includes(booking.status) && (
            <button onClick={handleCancel} className="btn-danger">Cancel Booking</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingDetails;
