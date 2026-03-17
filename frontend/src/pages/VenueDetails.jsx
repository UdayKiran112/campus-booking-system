import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { venueService } from '../services/venueService';
import toast from 'react-hot-toast';

const VenueDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [venue, setVenue] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVenueDetails();
  }, [id]);

  const loadVenueDetails = async () => {
    try {
      const [venueData, pricingData] = await Promise.all([
        venueService.getVenueById(id),
        venueService.getVenuePricing(id),
      ]);
      setVenue(venueData);
      setPricing(pricingData.pricing);
    } catch (error) {
      toast.error('Failed to load venue details');
    } finally {
      setLoading(false);
    }
  };

  const handleBookNow = () => {
    navigate('/bookings/create', { state: { venue } });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!venue) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">Venue not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{venue.name}</h1>
          <p className="text-gray-600 mt-1">{venue.location}</p>
        </div>
        <span className="inline-block px-4 py-2 bg-primary-100 text-primary-800 rounded-full font-medium">
          {venue.category_display}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Type</p>
                <p className="font-medium">{venue.venue_type_display}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Capacity</p>
                <p className="font-medium">{venue.capacity} people</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Ownership</p>
                <p className="font-medium">{venue.ownership_display}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Department</p>
                <p className="font-medium">{venue.department || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Operating Hours</p>
                <p className="font-medium">{venue.available_from} - {venue.available_to}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className={`font-medium ${venue.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {venue.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>

          {venue.description && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Description</h2>
              <p className="text-gray-700">{venue.description}</p>
            </div>
          )}

          {venue.facilities && venue.facilities.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Facilities</h2>
              <div className="flex flex-wrap gap-2">
                {venue.facilities.map((facility, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {facility}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Booking Panel */}
        <div className="lg:col-span-1">
          <div className="card sticky top-6">
            <h2 className="text-xl font-semibold mb-4">Booking Information</h2>
            
            {pricing && (
              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Type:</span>
                  <span className="font-medium">{pricing.payment_type}</span>
                </div>
                {pricing.base_price > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Base Price:</span>
                    <span className="font-medium">₹{pricing.base_price}</span>
                  </div>
                )}
                {pricing.security_deposit > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Security Deposit:</span>
                    <span className="font-medium">₹{pricing.security_deposit}</span>
                  </div>
                )}
                {pricing.payment_type === 'FREE' && (
                  <div className="text-green-600 font-medium">
                    Free for your role
                  </div>
                )}
              </div>
            )}

            <button
              onClick={handleBookNow}
              disabled={!venue.is_active}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {venue.is_active ? 'Book This Venue' : 'Venue Not Available'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VenueDetails;
